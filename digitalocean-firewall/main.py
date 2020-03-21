import os
import sys
import json
import requests

workdir = os.path.dirname(os.path.abspath(__file__))

with open("{}/settings.json".format(workdir), 'r') as f:
    r = f.read()
    conf = json.loads(r)

DO_URI = "https://api.digitalocean.com/v2/"
headers = {
    "Authorization": "Bearer {}".format(conf["TOKEN"]),
    "Content-Type": "application/json"
}

r = requests.get("{}account".format(DO_URI), headers=headers)
if r.status_code != 200:
    sys.exit("Invalid token")
userEmail = json.loads(r.text)["account"]["email"]


def get_my_ip():
    services = [
        "https://api.ipify.org",
        "https://api.my-ip.io/ip",
        "https://ipinfo.io/ip",
        "https://icanhazip.com/"
        "http://ip.42.pl/raw"
    ]
    for s in services:
        try:
            r = requests.get(s)
            if r.status_code == 200:
                return r.text.rstrip()
        except:
            pass
    sys.exit("Unable to get public IP")


def firewalls_list():
    """
    Get list of all firewalls
    """
    r = requests.get("{}firewalls".format(DO_URI), headers=headers)
    if r.status_code == 200:
        _r = json.loads(r.text)["firewalls"]
        if len(_r) > 0:
            for k in _r:
                print("Name: {}, ID: {}".format(k["name"], k["id"]))
        else:
            print("No firewalls exist on your account {}".format(userEmail))

    sys.exit("Could not get firewalls, exit")


def firewall_get(id):
    """Get firewall information for ID
    Get firewall ID by running firewalls_list() fnc or
    go to digitalocean.com -> Networking -> Firewalls -> Get ID from URL

    Arguments:
        id {str} -- firewall_id

    Returns:
        dict -- Firewall information as returned from DigitalOcean
    """

    r = requests.get("{}firewalls/{}".format(DO_URI, id), headers=headers)
    if r.status_code == 200:
        _r = json.loads(r.text)["firewall"]
        return _r
    sys.exit("Cannot get Firewall for ID: {}".format(id))


def firewall_update(id, data):
    """Update firewall information

    Arguments:
        id {str} -- firewall_id
        data {dict} -- firewall information

    Returns:
        bool -- True if succeded otherwise False
    """

    r = requests.put("{}firewalls/{}".format(DO_URI, id),
                     headers=headers,
                     data=json.dumps(data))
    if r.status_code == 200:
        return True
    return False


def find(lst, key, value):
    '''Helper fnc to get index in a list'''

    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return -1


def firewall_update_ssh(id):
    """Update firewall to include your (dynamic) public IP

    Arguments:
        id {str} -- firewall_id

    Returns:
        bool -- True if success otherwise False
    """

    fw = firewall_get(id)
    ip = get_my_ip()

    _i = find(fw['inbound_rules'], "ports", "22")
    _addr = fw['inbound_rules'][_i]['sources']['addresses']

    if ip in _addr:
        print("Already exists")
        sys.exit(0)

    _addr.append(ip)
    fw['inbound_rules'][_i]['sources']['addresses'] = _addr

    '''
    Get firewall return 0 in ports if all ports open, however
    Update firewall needs 'all' for all and empty for ICMP
    Below we update to expected values
    '''

    for k, d in enumerate(fw['outbound_rules']):
        if d['protocol'] == 'icmp':
            fw['outbound_rules'][k]['ports'] = ""
        elif d['ports'] == '0':
            fw['outbound_rules'][k]['ports'] = "all"

    return firewall_update(id, fw)


if __name__ == "__main__":
    firewall_update_ssh(conf['FIREWALL_ID'])
