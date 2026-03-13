from __future__ import annotations

import os
import netrc
from typing import TYPE_CHECKING

import xarray as xr
from dotenv import load_dotenv

from edhclient.core.config import edh_config

if TYPE_CHECKING:
    from typing import Optional


class EDHClient:

    HOST = edh_config.HOST
    USERNAME = edh_config.USERNAME

    def __init__(
        self, 
        edh_password: Optional[str] = None, 
        env_file: Optional[str] = None, 
        netrc_file: Optional[str] = None
    ) -> None:
        load_dotenv(dotenv_path=env_file)
        self.edh_password = self._resolve_password(edh_password, netrc_file)

    def _resolve_password(
            self,
            explicit_password: Optional[str],
            netrc_file: Optional[str]
        ) -> str:
        if explicit_password:
            return explicit_password

        env_password = os.getenv("EDH_PASSWORD")
        if env_password:
            return env_password

        try:
            n = netrc.netrc(netrc_file)
            auth_info = n.authenticators(self.HOST)
            if auth_info:
                return auth_info[2]
        except FileNotFoundError:
            pass
        except netrc.NetrcParseError as e:
            print(f"Warning: Malformed .netrc file: {e}")

        raise ValueError(
            "Authentication failed: Could not find EDH password from arguments, "
            "the 'EDH_PASSWORD' environment variable, or a .netrc file."
        )

    def _read_edh(self, edh_uri: str) -> xr.Dataset:
        return xr.open_dataset(
            f"https://{self.USERNAME}:{self.edh_password}@{self.HOST}/{edh_uri}",
            storage_options={"client_kwargs": {"trust_env": True}},
            chunks={"time": 1},
            engine="zarr",
        )

    def read_singles(self) -> xr.Dataset:
        return self._read_edh(edh_config.SINGLE_LEVELS)

    def read_pressure_levels(self) -> xr.Dataset:
        return self._read_edh(edh_config.PRESSURE_LEVELS)


edh_client = EDHClient()
