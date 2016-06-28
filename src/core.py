import urllib2, subprocess, os
import SimpleHTTPServer
import SocketServer
from multiprocessing import Process

class Core:
    wifi_config_file = "/etc/wpa_supplicant/wpa_supplicant.conf"

    def __init__(self,conf):
        self.conf = conf
        self.server = None

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
            os.chdir(os.path.join(self.conf["home"],'wcamera/server/'))
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
        if type(self.conf["annotations"]) is not :
            self.conf["annotations"] = False
        if type(self.conf["directory"]) is not str or os.path.isdir(self.conf["directory"]):
            self.conf["directory"] = "../detected/"
        if type(self.conf["home"]) is not str or os.path.isdir(self.conf["home"]):
            self.conf["home"] = "/home/pi/
