from __future__ import annotations

from typing import Literal, Annotated

from pydantic import ConfigDict, Field

from mixam_sdk.item_specification.enums.component_type import ComponentType
from mixam_sdk.item_specification.models.component_support import ComponentSupport
from mixam_sdk.utils.enum_json import enum_by_name, enum_dump_name


class EndPapersComponent(ComponentSupport):

    component_type: Literal[ComponentType.END_PAPERS] = Field(
        default=ComponentType.END_PAPERS,
        frozen=True
    )

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
        frozen=False,
        strict=True
    )

