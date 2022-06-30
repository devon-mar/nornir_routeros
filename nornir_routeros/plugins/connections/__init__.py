import ssl
from typing import Any, Dict, Optional

from nornir.core.configuration import Config
from routeros_api import RouterOsApiPool

CONNECTION_NAME = "routerosapi"


class RouterOsApi:
    """
    Connects to the RouterOS device using the RouterOS API (with SSL by default).
    """

    def open(
        self,
        hostname: Optional[str],
        username: Optional[str],
        password: Optional[str],
        port: Optional[int],
        platform: Optional[str],
        extras: Optional[Dict[str, Any]] = None,
        configuration: Optional[Config] = None,
    ) -> None:
        """
        Connect to the device and populate the attribute :attr:`connection` with
        the underlying connection.

        Args:
            extras: Extra arguments for :class:`RouterOsApiPool`.

                * In addition to :class:`RouterOsApiPool`'s ssl parameters, this plugin also supports
                  using ``ssl_ca_file`` to specify a root certificate bundle.
        """
        params = {
            "host": hostname,
            "username": username,
            "password": password,
            "port": port,
            "plaintext_login": True,
            "use_ssl": True,
        }

        if extras is not None and extras.get("use_ssl", True):
            ssl_ctx = ssl.create_default_context()

            ssl_verify = extras.get("ssl_verify", True)
            # Disabling ssl_verify implicitly disables ssl_verify_hostname.
            # ValueError: Cannot set verify_mode to CERT_NONE when check_hostname is enabled.
            ssl_ctx.check_hostname = (
                False
                if ssl_verify is False
                else extras.get("ssl_verify_hostname", True)
            )
            ssl_ctx.verify_mode = ssl.CERT_REQUIRED if ssl_verify else ssl.CERT_NONE
            if "ssl_ca_file" in extras:
                ssl_ctx.load_verify_locations(extras.pop("ssl_ca_file"))
            params["ssl_context"] = ssl_ctx

        extras = extras or {}
        params.update(extras)
        self._pool = RouterOsApiPool(**params)
        self.connection = self._pool.get_api()

    def close(self) -> None:
        """Close the connection with the device"""
        self._pool.disconnect()
