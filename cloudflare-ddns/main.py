#!/usr/bin/env python3

'''
This is a simple Dynamic DNS updater for Cloudflare domains

Rename/copy settings-example.json to settings.json (ignored in git)

Edit settings.json file with the following information:
    TOKEN = get your API token from CloudFlare
    ZONE_ID = You can find it in Cloudflare Overview tab of your domain
    NAME = List of name(s) of the record(s) you want to keep up to date

    Multiple zones can be defined in settings.json

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
        except Exception:
            pass
    sys.exit("Unable to get public IP")


myip = get_my_ip()


class Cloudflare:
    def __init__(self, token, zone_id, names):
        self.token = token
        self.zone_id = zone_id
        self.names = names

        self.headers = {"Authorization": "Bearer {}".format(self.token)}
        r = requests.get("{}user/tokens/verify".format(CF_ENDPOINT), headers=self.headers)
        if r.status_code != 200:
            sys.exit("Invalid token for zone: {}".format(self.zone_id))

    def get_dns_record(self, name, type):
        params = {"name": name, "type": type}
        r = requests.get("{}zones/{}/dns_records".format(CF_ENDPOINT, self.zone_id),
                         headers=self.headers,
                         params=params)
        if r.status_code == 200:
            _r = json.loads(r.text)["result"]
            if len(_r) > 0:
                return _r[0]
            else:
                return None

    def create_dns_record(self, type, name, content, ttl=1, proxied=True):
        data = {"type": type,
                "name": name,
                "content": content,
                "ttl": ttl,
                "proxied": proxied}
        self.headers["Content-Type"] = "application/json"
        r = requests.post("{}zones/{}/dns_records".format(CF_ENDPOINT, self.zone_id),
                          headers=self.headers,
                          data=json.dumps(data))
        if r.status_code == 200:
            print("Record {} {} created. Great success :)".format(name, content))
        else:
            print("Unable to create record {}: {}".format(name, r.text))

    def update_dns_record(self, identifier, type, name, content, ttl=1, proxied=True):
        data = {"type": type,
                "name": name,
                "content": content,
                "ttl": ttl,
                "proxied": proxied}
        self.headers["Content-Type"] = "application/json"
        r = requests.put("{}zones/{}/dns_records/{}".format(CF_ENDPOINT, self.zone_id, identifier),
                         headers=self.headers,
                         data=json.dumps(data))
        if r.status_code == 200:
            print("Record {} updated to {}. Great success :)".format(name, content))
        else:
            print("Uh oh, could not update {}; {}'(".format(name, r.text))

    def update_names(self):
        for name in self.names:
            record = self.get_dns_record(name, "A")

            if record is None:
                self.create_dns_record("A", name, myip, 1)
            elif record["content"] == myip:
                print("Record {} is already up to date {}, nothing to do here".format(name, myip))
            else:
                self.update_dns_record(
                    record["id"],
                    record["type"],
                    record["name"],
                    myip,
                    record["ttl"],
                    record["proxied"]
                )


def main():
    if "TOKEN" in conf:
        Cloudflare(conf["TOKEN"], conf["ZONE_ID"], conf["NAMES"]).update_names()
    else:
        for zone in conf:
            Cloudflare(zone["TOKEN"], zone["ZONE_ID"], zone["NAMES"]).update_names()


main()
