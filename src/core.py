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
