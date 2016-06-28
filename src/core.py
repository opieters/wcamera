import urllib2, subprocess, os.path

class Core:
    wifi_config_file = "/etc/wpa_supplicant/wpa_supplicant.conf"

    @staticmethod
    def setup_wifi_connection(ssid,psk):
        with open(Core.wifi_config_file,'a') as f:
            f.write("""network={
    ssid="%s"
    psk="%s"
}
""" % (ssid,psk))

    @staticmethod
    def check_connection():
        url = "https://github.com/opieters/wcamera"
        try:
            response = urllib2.urlopen("http://www.ugent.be",timeout=1)
        except urllib2.URLError:
            return False
        return True

    @staticmethod
    def update(home_dir):
        connected = Core.check_connection()
        if not connected:
            return False
        subprocess.Popen('git pull origin master', cwd=os.path.join(home_dir, 'wcamera/'),shell=True)
        return True
