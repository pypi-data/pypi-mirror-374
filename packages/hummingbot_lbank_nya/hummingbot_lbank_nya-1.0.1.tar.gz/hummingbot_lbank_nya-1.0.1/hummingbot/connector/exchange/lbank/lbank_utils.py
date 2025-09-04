from decimal import Decimal
from typing import Dict

from Crypto.PublicKey import RSA
from pydantic import Field, ConfigDict
from pydantic.types import SecretStr

from hummingbot.client.config.config_data_types import BaseConnectorConfigMap, ClientFieldData
from hummingbot.connector.exchange.lbank import lbank_constants as CONSTANTS
from hummingbot.connector.exchange.lbank.lbank_auth import LbankAuth
from hummingbot.core.data_type.trade_fee import TradeFeeSchema

DEFAULT_FEES = TradeFeeSchema(
    maker_percent_fee_decimal=Decimal("0.001"),
    taker_percent_fee_decimal=Decimal("0.001"),
)

CENTRALIZED = True

EXAMPLE_PAIR = "BTC-USDT"


class LbankConfigMap(BaseConnectorConfigMap):
    connector: str = "lbank"
    lbank_api_key: SecretStr = Field(
        default=...,
        json_schema_extra={
            "prompt":lambda cm: "Enter your LBank API key",
            "is_secure":True,
            "is_connect_key":True,
            "prompt_on_new":True,
        }
    )
    lbank_secret_key: SecretStr = Field(
        default=...,
        json_schema_extra={
            "prompt":lambda cm: "Enter your LBank secret key",
            "is_secure":True,
            "is_connect_key":True,
            "prompt_on_new":True,
        }
    )
    lbank_auth_method: str = Field(
        default=...,
        json_schema_extra={
            "prompt":lambda cm: (
                f"Enter your LBank API Authentication Method ({'/'.join(list(CONSTANTS.LBANK_AUTH_METHODS))})"
            ),
            "is_connect_key":True,
            "prompt_on_new":True,
        }
    )

    model_config = ConfigDict(title="lbank")


KEYS = LbankConfigMap.construct()
