#!/usr/bin/env python

ssid = "test.ssid"
psk = "test.psk"
wifi_config_file = "test.txt"#"/etc/wpa_supplicant/wpa_supplicant.conf"

from wifi import Cell, Scheme

# get all cells from the air
ssids = [cell.ssid for cell in Cell.all('wlan0')]

print(ssids)

with open(wifi_config_file,'a') as f:
    f.write("""network = {
    ssid="%s"
    psk="%s"
}
""" % (ssid,psk))
