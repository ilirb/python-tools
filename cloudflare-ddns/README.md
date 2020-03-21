# Cloudflare dynamic DNS updater

This is a simple Dynamic DNS updater for Cloudflare domains

1. Rename/copy settings-example.json to settings.json (ignored in git)

2. Edit settings.json file with the following information:
    - `TOKEN` - API token from CloudFlare
    - `ZONE_ID` - You can find it in Cloudflare Overview tab of your domain
    - `NAME` - List of name(s) of the record(s) you want to keep up to date

3. Requires Python 3 and `requests` library
    ```
    python -m pip install -r requirements.txt
    or
    python -m pip install requests
    ```


4. Example, scheduling to run every 10 minutes:
    ```
    crontab -e
    */10 * * * * /usr/bin/python3 /path/cloudflare-ddns/main.py
    ```