'''
GitHub Actions secrets API

Reference: https://developer.github.com/v3/actions/secrets/
'''

# import os
import sys
import click
import json
import requests
from nacl import encoding, public

BASEURL="https://api.github.com"

# Help text
TOKEN_HELP="GitHub access token OR set GITHUB_TOKEN=token environment variable"
OWNER_HELP="GitHub owner/org"
REPO_HELP="GitHub repository"
SECRET_NAME_HELP="Secret name"
SECRET_VALUE_HELP="Secret value"
ORG_HELP="Manage Organization secrets instead of repository"


# Helper functions
def encrypt(key: str, secret_value: str) -> str:
    """Encrypt a Unicode string using the public key."""
    public_key = public.PublicKey(key, encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode(), encoding.Base64Encoder())
    return encrypted.decode("utf-8")


def get_pub_key(owner: str, repo: str, token: str, org=False) -> dict:
    headers = {"Authorization": f"token {token}"}
    url = f"{BASEURL}/repos/{owner}/{repo}/actions/secrets/public-key"
    if org:
        url = f"{BASEURL}/orgs/{owner}/actions/secrets/public-key"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        sys.exit("Could not get public key")
    return json.loads(r.text)


@click.group()
def cli():
    pass


@cli.command()
@click.option('-o', '--owner', help=OWNER_HELP, required=True)
@click.option('-r', '--repo', help=REPO_HELP)
@click.option('-t', '--token', help=TOKEN_HELP, required=True, envvar='GITHUB_TOKEN')
@click.option('--org', help=ORG_HELP, is_flag=True)
def get(owner: str, repo: str, token: str, org: bool) -> dict:
    """
    Get secrets from a repo

    Values are not possible to retreive, only name, created and updated information
    """
    headers = {"Authorization": f"token {token}"}
    url = f"{BASEURL}/repos/{owner}/{repo}/actions/secrets"

    if org:
        url = f"{BASEURL}/orgs/{owner}/actions/secrets"
    else:
        if not repo: sys.exit("-r/--repo is required")

    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        sys.exit("Could not list secrets")
    print(json.dumps(json.loads(r.text), indent=4, sort_keys=True))


# TODO
# Add 'selected_repository_ids' option

@cli.command()
@click.option('-o', '--owner', help=OWNER_HELP, required=True)
@click.option('-r', '--repo', help=REPO_HELP)
@click.option('-s', '--secret', help=SECRET_NAME_HELP, required=True)
@click.option('-v', '--value', help=SECRET_VALUE_HELP, required=True)
@click.option('-t','--token', help=TOKEN_HELP,
              required=True, envvar='GITHUB_TOKEN')
@click.option('--org', help=ORG_HELP, is_flag=True)
@click.option('--visibility',
               type=click.Choice(['all', 'private', 'selected'])
             )
def create(owner, repo, secret, value, token, org, visibility) -> str:
    """Create a new secrets"""
    headers = {"Authorization": f"token {token}"}
    url = f"{BASEURL}/repos/{owner}/{repo}/actions/secrets/{secret}"

    if org:
        if not visibility: sys.exit('--visibility is required')
        url = f"{BASEURL}/orgs/{owner}/actions/secrets/{secret}"
    else:
        if not repo: sys.exit("-r/--repo is required")

    pub_key = get_pub_key(owner, repo, token, org)
    encrypted_value = encrypt(pub_key["key"], value)
    data = {"encrypted_value": encrypted_value, "key_id": pub_key["key_id"]}
    if org: data['visibility'] = visibility

    r = requests.put(url, headers=headers, data=json.dumps(data))
    if r.status_code == 201:
        print(f"Secret {secret} created")
    elif r.status_code == 204:
        print(f"Secret {secret} updated")
    else:
        sys.exit(f"Could not create/update secret {secret}. Response:\n{r.text}")


@cli.command()
@click.option('-o', '--owner', help=OWNER_HELP, required=True)
@click.option('-r', '--repo', help=REPO_HELP)
@click.option('-s', '--secret', help=SECRET_NAME_HELP, required=True)
@click.option('-t', '--token', help=TOKEN_HELP, required=True, envvar='GITHUB_TOKEN')
@click.option('--org', help=ORG_HELP, is_flag=True)
def delete(owner, repo, secret, token, org) -> dict:
    """Delete a secret"""
    headers = {"Authorization": f"token {token}"}
    url = f"{BASEURL}/repos/{owner}/{repo}/actions/secrets/{secret}"
    if org:
        url = f"{BASEURL}/orgs/{owner}/actions/secrets/{secret}"
    else:
        if not repo: sys.exit("-r/--repo is required")

    r = requests.delete(url, headers=headers)
    if r.status_code != 204:
        sys.exit(f"Could not delete secret {secret}")
    result = {
        "ok": r.ok,
        "status_code": r.status_code,
        "secret": secret,
        "action": "delete"
    }
    print(json.dumps(result, indent=4, sort_keys=True))


if __name__ == '__main__':
    cli()
