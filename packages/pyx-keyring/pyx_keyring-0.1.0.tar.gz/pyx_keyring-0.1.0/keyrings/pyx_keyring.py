import logging
import os
import subprocess

from keyring import backend, credentials

logger = logging.getLogger(__name__)

ALLOWED_SERVICES = (
    "api.pyx.dev",
    "files.astralhosted.com",
)


def validate_service(service: str) -> bool:
    return any(
        service.startswith(name) or service.startswith(f"https://{name}")
        for name in ALLOWED_SERVICES
    )


def token_from_uv_cli() -> str | None:
    try:
        result = subprocess.run(
            ["uv", "auth", "token", "pyx.dev"],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            check=True,
        )
    except FileNotFoundError:
        logger.warning("uv could not be found")
        return
    except subprocess.CalledProcessError as exc:
        err = exc.stderr.decode().strip().splitlines()[0]
        logger.warning(f"Failed to get token from uv: {err}")
        return

    if not result.stdout:
        err = result.stderr.decode().strip().splitlines()[0]
        logger.warning(f"Failed to get token from uv: {err}")
        return

    token = result.stdout.decode().strip()
    return token


def get_token(service: str) -> str | None:
    if not validate_service(service):
        return
    token = (
        os.getenv("PYX_AUTH_TOKEN") or os.getenv("PYX_API_KEY") or token_from_uv_cli()
    )
    if not token:
        logger.warning(
            f"No credentials found for {service} in `PYX_API_KEY`, `PYX_AUTH_TOKEN`, or `uv auth token`"
        )
    return token


class PyxKeyring(backend.KeyringBackend):
    priority = 9

    def get_password(self, service, username):
        return get_token(service)

    def set_password(self, service, username, password):
        raise NotImplementedError()

    def delete_password(self, service, username):
        raise NotImplementedError()

    def get_credential(self, service, username):
        token = get_token(service)
        if not token:
            return None
        return credentials.SimpleCredential("__token__", token)
