#!/usr/bin/python3

'''
This is a simple Dynamic DNS updater for Cloudflare domains

Rename/copy settings-example.json to settings.json (ignored in git)

Edit settings.json file with the following information:
    TOKEN = get your API token from CloudFlare
    ZONE_ID = You can find it in Cloudflare Overview tab of your domain
    NAME = List of name(s) of the record(s) you want to keep up to date

Requires Python 3 and "requests" library
    "python -m pip install -r requirements.txt" or
    "python -m pip install requests"


Example, scheduling to run every 10 minutes:
    crontab -e
    */10 * * * * /usr/bin/python3 /path/cloudflare-ddns/main.py
'''

import os
import sys
import json
import requests

workdir = os.path.dirname(os.path.abspath(__file__))

with open("{}/settings.json".format(workdir), 'r') as f:
    r = f.read()
    conf = json.loads(r)

CF_ENDPOINT = "https://api.cloudflare.com/client/v4/"
headers = {"Authorization": "Bearer {}".format(conf["TOKEN"])}

r = requests.get("{}user/tokens/verify".format(CF_ENDPOINT), headers=headers)
if r.status_code != 200:
    sys.exit("Invalid token")


def get_dns_record(name, type):
    params = {"name": name, "type": type}
    r = requests.get("{}zones/{}/dns_records".format(CF_ENDPOINT, conf["ZONE_ID"]),
                     headers=headers,
                     params=params)
    if r.status_code == 200:
        _r = json.loads(r.text)["result"]
        if len(_r) > 0:
            return _r[0]
    sys.exit("Could not get {} dns record, exit".format(name))


def update_dns_record(identifier, type, name, content, ttl=1, proxied="true"):
    data = {"type": type,
            "name": name,
            "content": content,
            "ttl": ttl,
            "proxied": proxied}
    headers["Content-Type"] = "application/json"
    r = requests.put("{}zones/{}/dns_records/{}".format(CF_ENDPOINT, conf["ZONE_ID"], identifier),
                     headers=headers,
                     data=json.dumps(data))
    if r.status_code == 200:
        return 0
    else:
        return 1


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


def main():
    myip = get_my_ip()
    for name in conf["NAMES"]:
        dns = get_dns_record(name=name, type="A")

        if dns["content"] == myip:
            print("Record {} is already up to date {}, nothing to do here".format(name, myip))
        else:
            r = update_dns_record(dns["id"],
                                  dns["type"],
                                  dns["name"],
                                  myip,
                                  dns["ttl"],
                                  dns["proxied"])
            if r == 0:
                print("Record {} updated to {}. Great success :)".format(name, myip))
            else:
                print("Uh oh, could not update {}, :'(".format(name))

main()
