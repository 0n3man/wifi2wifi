# wifi 2 wifi router with openvpn client connectivity

This repo is based on https://github.com/davidflanagan/wifi-setup. With
slight modification to David's code base. I set up a wifi 2 wifi router
with an openvpn client connection to provide access to media stored at my
house.  This give me the ability to use a firestick configured to access my
various media services while traveling, while also allowing the firestick to
access media stored at my house.  David's project brings up a wireless
access point and then allows you to configure that interface to provide
wifi connective to a local network.  As I already have an access point I don't 
need the access point part of the original capability.  However I still need a way to get
the second interface connected to the local network.  David's code provides a
web server and wifi configuration commands that enable configuring the second 
interface. This is how it works:

- The wifi2wifi pi is not connected to the local wifi network when it is first
  turned on. It starts by broadcasting its own wifi access point on the
  second wireles interface. This acccess point is used to access the web server on the pi. 
  The user connects their phone or laptop to the fire_tv_access access point 
  and thens using a web browser (not a native app!) to access
  the device at the URL http://172.16.33.1/. The
  user can select their desired wifi network for internet access and enter the password
  on a web page.  The entered response is then used to configred the second wifi interface
  to give internet access.

The code is Linux-specific, depends on systemd, and has only
been tested on a Raspberry Pi 3+. That said it should also work on other version of pi hardware.
I suspect it would also run on other arm based boards.  The only requirement is that the linux 
distribution uses hostapd, dhcpcd, dnsmasq and openvpn to work. You start by loading the raspberry pi
operating system.  You need command line access either vai a console or ssh.  If you plan to 
use ssh remember to put a file named ssh in the /boot partition of the micro sd prior to booting your pi.
You should do the normal pi configuration to set the timezone and keyboard.
Do not configure wifi.

For this build I used the internal pi wifi and a cudy wifi adaptor available here:
```
https://www.amazon.com/gp/product/B084FS7BWF/ref=ppx_yo_dt_b_asin_title_o01_s00?ie=UTF8&psc=1
```
Here are the steps I followed toconfigure and run this server.

### Step 1: Load the needed packages
```
$ sudo apt update
$ sudo apt upgrade
$ sudo apt install hostapd dnsmasq openvpn dkms
$ sudo apt autoremove
$ shutdown -r now
```
### Step 2: If you're using a realtek adaptor for your second wifi device
The cudy adaptor is based on realtek which isn't included in the base raspberry os install.
Install the realtek driver

```
$ sudo bash
# git clone "https://github.com/RinCat/RTL88x2BU-Linux-Driver.git" /usr/src/rtl88x2bu-git
# sed -i 's/PACKAGE_VERSION="@PKGVER@"/PACKAGE_VERSION="git"/g' /usr/src/rtl88x2bu-git/dkms.conf
# dkms add -m rtl88x2bu -v git
# dkms autoinstall
```
### Step 3: Enable the wifi access point on wlan0
Add the following lines to the bottom of the /etc/dnsmasq.conf file:
```
interface=wlan1
dhcp-range=172.16.33.100,172.16.33.150,255.255.255.0,24h
server=8.8.8.8
```
Add these lines to /ect/dhcpcd.conf:
```
interface wlan1
    static ip_address=172.16.33.1/24
    nohook wpa_supplicant
```
Create the file /etc/hostapd/hostapd.conf with these lines
```
country_code=US
interface=wlan1
# create 5GHz access point
hw_mode=a
channel=149
# limit the frequencies used to those allowed in the country
#ieee80211d=1
# 802.11ac and 802.11n support
ieee80211ac=1
ieee80211n=1
# QoS support required for full speed
wmm_enabled=1
# set up secure wifi access point
ssid=wifi_setup
# 1=wpa, 2=wep, 3=both
auth_algs=1
wpa=2
wpa_passphrase=YOUR_PASS_CODE
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP CCMP
rsn_pairwise=CCMP
```
In the above you need to change YOUR_PASS_CODE to whatever you want
the user to enter for the wifi password.  You may need to change
your country and channel depending on where you're running your pi.
The above build a 5GHz network on channel 149 as it's seems to see little
use in the US.  Enable the access point software and then reboot the sytem to verify
your access point came up.

```
$ sudo systemctl unmask hostapd
$ sudo shutdown -r now
```
Use your phone or laptop to verify you can access the fire_tv_access 
wifi network. This is not a fully functional network at this point so if 
you have an android phone you'll have to tell it to connect, even though
the network can't provide internet access.  I don't have an apple phone
so I'm not sure how that interaction would go.

### Step 3: Install node js
This project uses node js for the web server and wifi configuration
server.  Use the following commands to install it:
```
$ sudo bash
# curl -fsSL https://deb.nodesource.com/setup_17.x | bash -
# apt install nodejs
# exit
$ node --version
$ npm --version
```
### Step 4: clone and install

First, clone this repo and set it up to start on boot. Also we have a 
service that clears out previous wifi connection information at boot.
As such everytime you reboot the pi you need to connect to the web 
service and configure your wifi access.
```
$ git clone https://github.com/0n3man/wifi2wifi
$ cd wifi2wifi
$ sudo cp config/wifi-setup.service /lib/systemd/system
$ sudo vi /lib/systemd/system/wifi-setup.service # edit paths as needed
$ sudo systemctl enable wifi-setup
$ sudo cp net-configs/clear_wpa_config.service /lib/systemd/system
$ sudo vi /lib/systemd/system/clear_wpa_config.service # edit paths as needed
$ sudo systemctl enable clear_wpa_config.service
```
Once we've connected to a wifi service we'll need to to have iptables masquade.
Add these lines to the end of the /etc/rc.local file just before the exit 0 line:
```
iptables -t nat -A  POSTROUTING -o eth0 -j MASQUERADE
iptables -t nat -A  POSTROUTING -o wlan0 -j MASQUERADE
iptables -t nat -A  POSTROUTING -o tun0 -j MASQUERADE
```
We also need to enable nic to nic routing so edit the file /etc/sysctrl.conf
and uncomment this line by removing the # in front of it.
```
net.ipv4.ip_forward=1
```
You can reload this setting via:
```
$ sudo sysctl --system
```
Before we reboot we can test that the web server will come up.  If the netstat 
command below provides output you have a web server listening on port 80. 
```
$ sudo systemctl daemon-reload
$ sudo systemctl start wifi-setup
$ sudo netstat -lntp | grep ":80"
```
At this point you could use your phone to access the webserver at https://172.16.33.1/
and configure the wifi internet connectivity.

### Step 6: Add a flashing light to show progress
I connected an led to pins 6 and 8. Depending on your led you might need a resister, but
the one I used seems to work just fine.  I add the following line to the end of /etc/rc.local just
before the exit 0
```
/home/pi/wifi2wifi/net-configs/gpio_status.py > /dev/null&
```
The light will be on solid if the web server is up and running.  It will flash while the
wifi interent service is being conigured.  Once the box can ping 8.8.8.8, meaning you have internet
access, the light will stop flashing.  


### Step 5: Add in openvpn connection to access your own content
You need to generate a openvpn configuration on your openvpn server.  Then you put the .key and .p12
files in /etc/openvpn/client directory.  You then place your openvpn configuration file in the
/etc/openvpn directory and make sure the name ends with ".conf".  So my /etc/openvpn/tv_client.conf 
file looks like this:
```
dev tun
persist-tun
persist-key
cipher AES-128-CBC
auth SHA1
client
resolv-retry infinite
remote MYDOMAIN.com 21949 udp
lport 0
verify-x509-name "C=US, ST=MYSTATE, L=MYCITY, O=home, emailAddress=WHATEVE@gmail.com, CN=VPNCert" subject
remote-cert-tls server
pkcs12 /etc/openvpn/client/Moms_VPN_access_tv_access.p12
tls-auth /etc/openvpn/client/Moms_VPN_access_tv_access-tls.key 1
float
```
The float line at the end is probably not reequired in most cases.  I included because I was having
a problems where my test router NATs the openvpn return traffic.  So responses for openvpn
were coming from the wrong IP address. The float line tells openvpn to access these responses.  

The last thing to do is to set the vpn to start by editing /etc/defaults/openvpn.  You need to add the line:
```
AUTOSTART="tv_client"
```
The name here tv_client matches the name of the file we just created in /etc/openvpn.

With the above in place you can restart openvpn
```
systemctl daemon-reload
systemctl restart openvpn
```
if all goes well with the vpn connection you should have a tun0 interface giving you access to whatever is
at the other end of the tunnel.






