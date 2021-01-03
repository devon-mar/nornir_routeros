from typing import Any, Dict, Optional
from nornir.core.configuration import Config
from nornir.core.plugins.connections import ConnectionPlugin
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
        """
        params = {
            "host": hostname,
            "username": username,
            "password": password,
            "port": port,
            "plaintext_login": True,
            "use_ssl": True,
        }
        extras = extras or {}
        params.update(extras)
        self._pool = RouterOsApiPool(**params)
        self.connection = self._pool.get_api()

    def close(self) -> None:
        """Close the connection with the device"""
        self._pool.disconnect()
