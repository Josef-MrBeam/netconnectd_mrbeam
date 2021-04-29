**INSTALLATION**

* Create a Python 3 venv - the included service unit expects the venv to be in /usr/local/netconnectd/venv and activate it.
* Install `wifi` from `https://github.com/ManuelMcLure/wifi.git` branch `master`
* Install `netconnectd_mrbeam` from `https://github.com/ManuelMcLure/netconnectd_mrbeam.git` branch `master`.
* Copy `netconnectd.yaml` from `extras` to the `/etc/netconnectd.conf.d/` directory.
* Copy `netconnectd.service` from `extras` to the `/etc/systemd/system/` directory
* Enable the netconnectd systemd unit with
  ```
  systemctl enable netconnectd.service
  ```
* Disable the `dnsmasq` and `wpa_supplicant` services:
  ```
  systemctl disable dnsmasq.service
  systemctl disable wpa_supplicant
  ```
* Copy `eth0` from `extras` to the `/etc/network/interfaces.d/` directory.
* Start the daemon with
  ```
  systemctl start netconnectd.service
  ```
* Install into your OctoPrint venv the version of `OctoPrint-Netconectd` from `https://github.com/ManuelMcLure/OctoPrint-Netconnectd.git` branch `master`.
