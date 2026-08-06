import ipaddress
import re
from typing import Optional

import click

INVALID_KEY_MSG = click.style("Your encryption 🔑 is invalid.", fg="red")

INVALID_MAC_MSG = click.style("{} is not a valid mac address.", fg="red")

INVALID_IPV4_MSG = click.style("{} is not a valid ipv4 address.", fg="red")


class KeyParamType(click.ParamType):
    name = "key"

    def _check_key(self, key: str) -> bool:
        from pyencrypt.utils import check_key

        return check_key(key)

    def convert(self, value, param, ctx) -> str:
        from click.core import ParameterSource  # click>=8

        if ctx.get_parameter_source(param.name) == ParameterSource.ENVIRONMENT:
            visible_chars = 4
            masked = (
                value[:visible_chars]
                + "*" * (len(value) - 2 * visible_chars)
                + value[-visible_chars:]
            )
            click.echo(
                f'Using encryption key 🔑 {click.style(masked, fg="yellow")} from environment variable {click.style(param.envvar, fg="bright_cyan")}.'
            )

        value = click.STRING.convert(value, param, ctx)
        if not self._check_key(value):
            self.fail(INVALID_KEY_MSG, param, ctx)
        return value

    def get_metavar(self, param: click.Parameter, ctx: Optional[click.Context] = None):
        return "🔑"

    def __repr__(self) -> str:
        return "KEY"


class MacAddressParamType(click.ParamType):
    name = "mac_address"
    pattern = re.compile(r"^([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})$")

    def convert(self, value, param, ctx) -> str:
        value = click.STRING.convert(value, param, ctx)
        if not self.pattern.match(value):
            self.fail(INVALID_MAC_MSG.format(value), param, ctx)
        return value

    def get_metavar(self, param: click.Parameter, ctx: Optional[click.Context] = None):
        return "01:23:45:67:89:AB"

    def __repr__(self) -> str:
        return "MacAddress"


class IPv4AddressParamType(click.ParamType):
    name = "ipv4_address"

    def convert(self, value, param, ctx) -> str:
        value = click.STRING.convert(value, param, ctx)
        try:
            return str(ipaddress.IPv4Address(value))
        except ValueError:
            self.fail(INVALID_IPV4_MSG.format(value), param, ctx)

    def get_metavar(self, param: click.Parameter, ctx: Optional[click.Context] = None):
        return "192.168.0.1"

    def __repr__(self) -> str:
        return "Ipv4Address"


class CustomParamType:
    KEY = KeyParamType()
    MAC_ADDR = MacAddressParamType()
    IPV4_ADDR = IPv4AddressParamType()
