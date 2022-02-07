# wifi-setup

This repo is based on https://github.com/davidflanagan/wifi-setup. With
slight modification to David's code base. I set up a wifi 2 wifi router
with an openvpn client connection to provide access to media stored at my
house.  This give me the ability to use a firestick configured to access my
various media services while traveling, while also allowing the firestick to
access media stored at my house.  David's project brings up a wireless
access point and then allows you to configure that interface to provide
wifi connective to a local network.  As I already have an access point I don't 
need that part of the original capability.  However I still need a way to get
the second interface connected to the local network.  David's code provides the
web server and wifi configuration commands that enable configuring the second 
interface.

- since the device is not on the local wifi network when it is first
  turned on, the device broadcasts its own wifi access point and runs
  the server on that. The user then connects their phone or laptop to
  that wifi network and uses a web browser (not a native app!) to
  connect to the device at the URL 172.16.33.1 or `<hostname>.local`. The
  user can select then their home wifi network and enter the password
  on a web page and transfer it to the web server running on the
  device. At this point the device connects the second wifi interface
  to the internet using the credentials the user provided.

The code is Linux-specific, depends on systemd, and has so far only
been tested on a Raspberry Pi 3. The complete package hostapd, dhcpcd,
dnsmasq and openvpn to be installed and properly configured. wlan1 must be
configured as a wifi access point.  

Here are the steps I followed toconfigure and run this server.

### Step 0: clone and install

First, clone this repo and download its dependencies from npm:

```
$ git clone https://github.com/0n3man/wifi2wifi
$ cd wifi2wifi
$ !!!! node install instructions
```

### Step 1: install needed networking package

Install software we need to host an access point. For Raspberry
Pi, we need to do:

```
$ sudo apt-get install hostapd
$ sudo apt-get install dnsmasq
$ sudo apt-get install openvpn
```

### Need to update everything after here
### Step 2: configuration files
Next, configure the software:

- Edit /etc/default/hostapd to add the line:

```
DAEMON_CONF="/etc/hostapd/hostapd.conf"
```

- Copy `config/hostapd.conf` to `/etc/hostapd/hostapd.conf`.  This
  config file defines the access point name "Wifi Setup". Edit it if
  you want to use a more descriptive name for your device.

- Edit the file `/etc/default/udhcpd` and comment out the line:

```
DHCPD_ENABLED="no"
```

- Copy `config/udhcpd.conf` to `/etc/udhcp.conf`.

### Step 3: set up the other services you want your device to run

Once the wifi-setup server has connected to wifi, it will exit. But if
you want, it can run a command to make your device start doing
whatever it is your device does. If you want to use this feature, edit
`platforms/default.js` to define the `nextStageCommand` property.

### Step 4: run the server

If you have a keyboard and monitor hooked up to your device, or have a
serial connection to the device, then you can try out the server at
this point:

```
sudo node index.js
```

If you want to run the server on a device that has no network
connection and no keyboard or monitor, you probably want to set it up
to run automatically when the device boots up. To do this, copy
`config/wifi-setup.service` to `/lib/systemd/system`, edit it to set
the correct paths for node and for the server code, and then enable
the service with systemd:

```
$ sudo cp config/wifi-setup.service /lib/systemd/system
$ sudo vi /lib/systemd/system/wifi-setup.service # edit paths as needed
$ sudo systemctl enable wifi-setup
```

At this point, the server will run each time you reboot.  If you want
to run it manually without rebooting, do this:

```
$ sudo systemctl start wifi-setup
```

Any output from the server is sent to the systemd journal, and you can
review it with:

```
$ sudo journalctl -u wifi-setup
```

Add the -b option to the line above if you just want to view output
from the current boot.  Add -f if you want to watch the output live as
you interact with the server.

If you want these journals to persist across reboots (you probably do)
then ensure that the `/var/log/journal/` directory
exists:

```
$ sudo mkdir /var/log/journal
```
