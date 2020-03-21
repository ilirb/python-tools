# DigitalOcean add dynamic IP in firewall

Keep DigitalOcean SSH Firewall up to date when client has dynamic IP address

1. Rename/copy settings-example.json to settings.json (ignored in git)

2. Edit settings.json file with the following information:
    - `TOKEN` - API token from DigitalOcean
    - `FIREWALL_ID` - Get firewall ID by running firewalls_list() function or login to Digitalocean.com -> Networking -> Firewalls -> Get ID from URL

3. Example, scheduling to run every 10 minutes:
    ```
    crontab -e
    */10 * * * * /usr/bin/python3 /path/digitalocean-firewall/main.py
    ```
