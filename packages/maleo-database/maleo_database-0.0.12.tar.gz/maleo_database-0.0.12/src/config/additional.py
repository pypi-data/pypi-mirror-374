from pydantic import BaseModel, Field
from typing import Optional, TypeVar, Union
from maleo.enums.cache import Origin, Layer
from maleo.enums.expiration import Expiration
from maleo.types.base.string import OptionalString
from maleo.utils.cache import build_namespace as build_namespace_utils


class BaseAdditionalConfig(BaseModel):
    """Base additional configuration class for database."""


AdditionalConfigT = TypeVar("AdditionalConfigT", bound=Optional[BaseAdditionalConfig])


class RedisAdditionalConfig(BaseAdditionalConfig):
    ttl: Union[float, int] = Field(
        Expiration.EXP_15MN.value, description="Time to live"
    )
    base_namespace: str = Field(..., description="Base namespace")

    def build_namespace(
        self,
        *ext: str,
        base: OptionalString = None,
        client: OptionalString = None,
        origin: Origin,
        layer: Layer,
        sep: str = ":",
    ) -> str:
        base = base or self.base_namespace
        return build_namespace_utils(
            *ext, base=base, client=client, origin=origin, layer=layer, sep=sep
        )
