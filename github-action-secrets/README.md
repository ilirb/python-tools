# GitHub Actions secrets cli

A cli script for managing GitHub secrets

`get` - Get a list of all secrets from a repo (name, create, updated)

`create` - Create or update a secret

`delete` - Delete a secret

1. Install requirements
    ```
    python -m pip install -r requirements.txt
    ```

2. Run
    ```
    python gh.py --help
    ```

GitHub access token with repo scope is required to run this script.

Either pass it as option in cli `--token <mytoken>` or set environment variable and ommit the parameter
```
*nix
    export GITHUB_TOKEN=<mytoken>

windows:
    set GITHUB_TOKEN=<mytoken>
```