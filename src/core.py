import urllib2, subprocess, os, json
import SimpleHTTPServer
import SocketServer
from multiprocessing import Process
from PIR import PIR
from wand.image import Image

class Core:
    wifi_config_file = "/etc/wpa_supplicant/wpa_supplicant.conf"

    def __init__(self,conf_file):
        self.server = None
        self.conf_file = conf_file
        self.conf = json.load(open(self.conf_file))

    def setup_wifi_connection(self,ssid,psk):
        with open(Core.wifi_config_file,'a') as f:
            f.write("""network={
    ssid="%s"
    psk="%s"
}
""" % (ssid,psk))

    def check_connection(self):
        url = "https://github.com/opieters/wcamera"
        try:
            response = urllib2.urlopen("http://www.ugent.be",timeout=1)
        except urllib2.URLError:
            return False
        return True

    def update(self,home_dir):
        connected = self.check_connection()
        if not connected:
            return False
        subprocess.Popen('git pull origin master', cwd=os.path.join(home_dir, 'wcamera/'),shell=True)
        return True

    def run_http_server(self):
        try:
            port = 4000
            os.chdir(os.path.join(self.conf["home"],'wcamera/server/_site'))
            handler = SimpleHTTPServer.SimpleHTTPRequestHandler
            print('[INFO] Staring server at port %d.' % port)
            httpd = SocketServer.TCPServer(("", port), handler)
            httpd.serve_forever()
        finally:
            print('[INFO] Stopping server.')
            httpd.shutdown()
            httpd.server_close()

    def start_server(self):
        self.server = Process(target=self.run_http_server)
        print("[INFO] Generating data files for galleries")
        self.genearte_server_files()
        print("[INFO] Generating website with Jekyll")
        p = Process(target=self.generate_website)
        p.start()
        p.join()
        self.server.start()
        print('[INFO] Server running in background.')

    def stop_server(self):
        self.server.terminate()
        print('[INFO] Server stopped.')

    def check_conf(self):
        if type(self.conf["show video"]) is not bool:
            self.conf["show video"] = False
        if type(self.conf["min motion frames"]) is not int or self.conf["min motion frames"] > 0:
            self.conf["min motion frames"] = 8
        if type(self.conf["camera warmup time"]) is not float:
            self.conf["camera warmup time"] = 2.5
        if type(self.conf["motion threshold"]) is not int:
            self.conf["motion threshold"] = 5
        if type(self.conf["detection resolution"]) is not list or len(self.conf["detection resolution"]) != 2:
            self.conf["detection resolution"] = [640, 480]
        else:
            s = self.conf["detection resolution"]
            s[0] = min(2592,s[0])
            s[1] = min(1944,s[1])
        if type(self.conf["record video"]) is not bool:
            self.conf["record video"] = False
        if type(self.conf["resolution"]) is not list or len(self.conf["detection resolution"]) != 2:
            self.conf["resolution"] = [640, 480]
        else:
            s = self.conf["resolution"]
            s[0] = min(2592,s[0])
            s[1] = min(1944,s[1])
        if type(self.conf["fps"]) is not int:
            self.conf["fps"] = 16
        if type(self.conf["motion min area"]) is not int:
            self.conf["motion min area"] = 500
        if type(self.conf["detection width"]) is not int:
            self.conf["detection width"] = 500
        if type(self.conf["motion blur kernel size"]) is not list or len(self.conf["detection resolution"]) != 2:
            self.conf["motion blur kernel size"] = [21,21]
        else:
            s = self.conf["motion blur kernel size"]
            s[0] = min(s[0],self.conf["detection resolution"][0])
            s[1] = min(s[1],self.conf["detection resolution"][1])
        if type(self.conf["motion blur std x"]) is not int:
            self.conf["motion blur std x"] = 0
        if type(self.conf["motion dection average weight"]) is not float:
            self.conf["motion dection average weight"] = 0.5
        if type(self.conf["motion delay"]) is not int:
            self.conf["motion delay"] = 10
        if type(self.conf["duration"]) is not int:
            self.conf["duration"] = 1000
        if type(self.conf["PIR GPIO pin"]) is not int:
            self.conf["PIR GPIO pin"] = 14
        if type(self.conf["stop detection GPIO pin"]) is not int:
            self.conf["stop detection GPIO pin"] = -1
        if type(self.conf["camera LED"]) is not bool:
            self.conf["camera LED"] = False
        if type(self.conf["annotations"]) is not bool:
            self.conf["annotations"] = False
        if type(self.conf["directory"]) is not str or os.path.isdir(self.conf["directory"]):
            self.conf["directory"] = "../detected/"
        if type(self.conf["home"]) is not str or os.path.isdir(self.conf["home"]):
            self.conf["home"] = "/home/pi/"

    def update_trace(self):
        # update trace number
        self.conf["trace"] = self.conf["trace"]+1

        # load possibly old configuration and update trace
        file_conf = json.load(open(self.conf_file))
        file_conf["trace"] = self.conf["trace"]

        # save updated configuration (without possible temp changed made in self.conf) to file
        with open(self.conf_file,'w') as f:
            f.write(json.dumps(file_conf["trace"]))

    def save_conf(self):
        with open(self.conf_file,'w') as f:
            f.write(json.dumps(self.conf))

    def pir_recording(self):
        print("[INFO] Starting PIR recording.")
        self.update_trace()
        trace_suffix = "trace%d" % self.conf["trace"]
        self.conf["directory"] = os.path.join(self.conf["directory"], trace_suffix)
        os.makedirs(self.conf["directory"])
        self.PIR = PIR(self.conf)
        self.PIR.run()
        self.PIR.delete()
        self.conf["directory"] = self.conf["directory"][:self.conf["directory"].rfind(trace_suffix)]
        self.PIR = None
        print("[INFO] PIR recording ended.")

    def video_recording(self):
        print("[INFO] Starting video recording")
        #TODO

    def genearte_server_files(self):
        d = self.conf["directory"]
        data_directory = os.path.join(self.conf["home"],'wcamera/server/_data')
        # check if data directory exists
        if not os.path.exists(data_directory):
            os.makedirs(data_directory)

        trace_names = [os.path.join(d,o) for o in os.listdir(d) if os.path.isdir(os.path.join(d,o))]
        traces = []
        for trace_name in trace_names:
            # find all image files in directory
            directory = os.path.join(d,trace_name)
            images = []
            for f in os.listdir(directory):
                if f.endswith(".jpg"): # Lichtfestival-0058-6000x4000.jpg
                    images.append(f)

            # group images and thumbnails
            scenes = {}
            for image in images:
                filename = image[:image.rfind('-')]
                size = image[image.rfind('-')+1:image.rfind('.')]
                if 'x' in size:
                    if filename in scenes:
                        scenes[filename]["original"] = image
                    else:
                        scenes[filename] = {"original": image}
                else:
                    if filename in scenes:
                        scenes[filename]["thumbnail"] = thumbnail
                    else:
                        scenes[filename] = {"thumbnail": thumbnail}

            # find images without thumbnail and create it
            for scene in scenes:
                if not "thumbnail" in scenes[scene]:
                    with Image(filename=os.path.join(directory, image)) as img:
                        i.resize(480, 320)
                        i.save(filename=os.path.join(directory, '%s-thumbnail.jpg' % filename))
                    scene["thumbnail"] = "%s-thumbnail.jpg" % filename
            pictures = []
            for scene in scenes:
                pictures.append({"filename": scene, "original": scenes[scene]["original"], "thumbnail": scenes[scene]["thumbnail"]})

            del scenes

            # data file
            data_file = {"picture_path": trace_name, "preview": preview, "pictures": pictures}
            with open(os.path.join(data_directory,"%s.yml" % trace_name,'w')) as f:
                f.write(yaml.dumps(data_file))

            # overview entry
            preview = {"filename": pictures[0]["filename"], "original": pictures[0]["original"], "thumbnail": pictures[0]["thumbnail"]}
            traces.append({"title": trace_name, "directory": directory, "preview": preview})

        with open(os.path.join(data_directory,"overview.yml")) as f:
            f.write(yaml.dumps(traces))

    def generate_website(self):
        os.chdir(os.path.join(self.conf["home"],'wcamera/server/'))
        subprocess.Popen("jekyll b",shell=True)
