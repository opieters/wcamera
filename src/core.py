import urllib2, subprocess, os, json, yaml
import SimpleHTTPServer
import SocketServer
from multiprocessing import Process
from PIR import PIR
from wand.image import Image
from picamera import PiCamera, PiCameraError
from motion_detector import MD

class Core:
    wifi_config_file = "/etc/wpa_supplicant/wpa_supplicant.conf"

    def __init__(self,conf_file):
        self.server = None
        self.conf_file = conf_file
        self.conf = json.load(open(self.conf_file))
        self.tmp = {}
        self.camera = PiCamera()

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
        subprocess.call('git pull origin master', cwd=os.path.join(home_dir, 'wcamera/'),shell=True)
        return True

    def run_http_server(self):
        port = 4000
        os.chdir(os.path.join(self.conf["home"],'server/_site'))
        handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        print('[INFO] Staring server at port %d.' % port)
        httpd = SocketServer.TCPServer(("", port), handler)
        try:
            httpd.serve_forever()
        finally:
            print('[INFO] Stopping server.')
            httpd.shutdown()
            httpd.server_close()

    def start_server(self):
        self.server = Process(target=self.run_http_server)
        print("[INFO] Generating data files for galleries")
        self.generate_server_files()
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
            self.conf["home"] = "/home/pi/wcamera"

    def update_trace(self):
        # update trace number
        self.conf["trace"] = self.conf["trace"]+1
        print(self.conf["trace"])

        # load possibly old configuration and update trace
        file_conf = json.load(open(self.conf_file))
        print(file_conf)
        file_conf["trace"] = self.conf["trace"]

        # save updated configuration (without possible temp changed made in self.conf) to file
        with open(self.conf_file,'w') as f:
            json.dump(file_conf,f)

    def save_conf(self):
        with open(self.conf_file,'w') as f:
            json.dump(self.conf,f)

    def pir_recording(self):
        print("[INFO] Starting PIR recording.")
        self.update_trace()
        trace_suffix = "trace%d/" % self.conf["trace"]
        self.conf["directory"] = os.path.join(self.conf["directory"], trace_suffix)
        if not os.path.exists(self.conf["directory"]):
            os.mkdir(self.conf["directory"])
        print(self.conf["directory"])
        self.PIR = PIR(self.camera,self.conf)
        self.PIR.run()
        self.PIR.delete()
        self.conf["directory"] = self.conf["directory"][:self.conf["directory"].rfind(trace_suffix)]
        self.PIR = None
        print("[INFO] PIR recording ended.")

    def video_recording(self):
        print("[INFO] Starting video recording")
        md = MD(self.camera, self.conf)

    def generate_server_files(self):
        image_directory = os.path.join(self.conf["home"], self.conf["directory"])
        data_directory = os.path.join(self.conf["home"],'server/_data/')
        html_directory = os.path.join(self.conf["home"],'server/gallery/')
        # check if data directory exists
        if not os.path.exists(data_directory):
            os.makedirs(data_directory)

        trace_directories = [os.path.join(image_directory,d) for d in os.listdir(image_directory) if os.path.isdir(os.path.join(image_directory,d))]
        traces = []
        for directory in trace_directories:
            # find all image files in directory
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
                        scenes[filename]["thumbnail"] = image
                    else:
                        scenes[filename] = {"thumbnail": image}

            # find images without thumbnail and create it
            for scene in scenes:
                if not "thumbnail" in scenes[scene]:
                    with Image(filename=os.path.join(directory, image)) as i:
                        i.resize(480, 320)
                        i.save(filename=os.path.join(directory, '%s-thumbnail.jpg' % scene))
                    scenes[scene]["thumbnail"] = "%s-thumbnail.jpg" % scene
            pictures = []
            for scene in scenes:
                caption = scene[scene.find('-')+1:]
                pictures.append({"filename": scene, "original": scenes[scene]["original"], "thumbnail": scenes[scene]["thumbnail"], "title": caption})

            del scenes

            # sort pictures by date
            pictures.sort(key=lambda x: x["title"])

            if directory[-1] == '/':
                directory = directory[:-1]
            trace_name = directory[directory.rfind('/')+1:]

            # html file
            with open(os.path.join(html_directory,trace_name+".html"),'w') as f:
                f.write("---\n")
                f.write("layout: default\n")
                f.write("title: %s\n\n" % trace_name)
                f.write("---\n")
                f.write("{% include gallery-layout.html gallery=site.data."+trace_name+" %}\n")



            # overview entry
            if len(pictures) > 0:
                preview = {"filename": pictures[0]["filename"], "original": pictures[0]["original"], "thumbnail": pictures[0]["thumbnail"]}
                traces.append({"title": trace_name, "directory": trace_name, "preview": preview})

                # data file
                data_file = {"picture_path": trace_name, "preview": preview, "pictures": pictures}
                with open(os.path.join(data_directory,"%s.yml" % trace_name),'w') as f:
                    f.write(yaml.safe_dump(data_file,default_flow_style=False))

        with open(os.path.join(data_directory,"overview.yml"),'w') as f:
            f.write(yaml.safe_dump(traces,default_flow_style=False))

    def generate_website(self):
        os.chdir(os.path.join(self.conf["home"],'server/'))
        subprocess.call("jekyll b",shell=True)

    def delete(self):
        self.camera.close()

    def start_hotspot(self):
        subprocess.call("sudo ifconfig wlan0 192.168.42.1",shell=True)
        subprocess.call("sudo service hostapd start",shell=True)
        subprocess.call("sudo service udhcpd start",shell=True)

    @staticmethod
    def get_connected_devices():
        output =  subprocess.check_output("sudo blkid",shell=True)
        dev_list, devices = output.split('\n'), []
        for dev in dev_list:
            devices.append(dev[:dev.find(":")]) if ':' in dev else ''
        return devices

    def before_usb_inserted(self):
        self.tmp["usb list"] = Core.get_connected_devices()

    def copy_to_usb(self):
        if "usb list" not in self.tmp:
            print('[INFO] Unable to find usb device list before drive insertion.')
            return False

        data_path = os.path.join(self.conf["home"],'server/_data/')  # folder with traces
        prev = self.tmp["usb list"]  # list of devices that were connected before drive was plugged in

        devices = Core.get_connected_devices()  # get list of usb devices with drive

        # find drive (assumed to be first newly connected device)
        drive = None
        for dev in devices:
            if not dev in prev:
                drive = dev
                break
        if drive is None:
            print('[INFO] unable to find drive')
            return False

        # find a mountpoint
        mount, cnt = "/media/usb", 0
        while os.path.isdir(mount + str(cnt)):
            cnt += 1

        # mount device
        mount = mount + str(cnt)
        os.makedirs(mount)
        subprocess.call('sudo mount %s %s' % (drive,mount), shell=True)

        buffer_space = int(100*1e6) # 100MB free space

        # get directory structure
        dirs = [f for f in os.listdir(data_path) if os.path.isdir(os.path.join(data_path, f))]

        # create directories
        for d in dirs:
            usb_dir = os.path.join(mount,d)
            src_dir = os.path.join(data_path,d)
            if not os.path.isdir(usb_dir):
                os.mkdir(usb_dir)

            files = [f for f in os.listdir(src_dir) if os.path.isfile(os.path.join(src_dir,f))]

            for f in files:
                file_dir = os.path.join(src_dir,f)

                # get free space
                statvfs = os.statvfs(mount)
                free_space = statvfs.f_frsize * statvfs.f_bavail

                # check if enough free space
                if free_space > buffer_space and os.path.getsize(file_dir) < free_space:
                    shutil.move(file_dir, os.path.join(usb_dir,f))
                    print '[INFO] moved', f
                else:
                    print('[INFO] Not enough space')
                    return False

        return True
