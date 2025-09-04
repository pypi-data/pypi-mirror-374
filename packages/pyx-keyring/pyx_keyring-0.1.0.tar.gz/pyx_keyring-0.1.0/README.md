# pyx-keyring

Authenticates with `pyx` using a `keyring` plugin.

Retrieves a token from `PYX_AUTH_TOKEN` or `PYX_API_KEY` if set. Otherwise, fetches a token from `uv auth token pyx.dev`.

To install with pip:

```
# Create a virtual environment.
python -m venv .venv
source .venv/bin/activate

# Install keyring and the pyx-keyring plugin.
pip install keyring
pip install git+https://github.com/astral-sh/pyx-keyring

# Install from pyx.
pip install fastapi --index-url https://api.pyx.dev/simple/pypi
```
