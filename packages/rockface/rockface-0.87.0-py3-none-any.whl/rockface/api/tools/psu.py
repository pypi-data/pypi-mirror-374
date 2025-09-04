from enum import Enum
from math import isclose

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Annotated

from ...api.tool_request import ToolRequest


class CurrentLimitMode(str, Enum):
    """The behaviour of a PSU tool when the current limit is reached

    LIMIT: The power supply will enter into "constant current" mode
           if the limit is reached -- i.e. it will reduce the voltage
           it is delivering to the load to keep the current below the
           limit.
    TRIP: If the current delivered to the load exceeds the limit, then
          the power supply will turn off."""

    LIMIT = "limit"
    TRIP = "trip"


class CurrentLimitModeParams(ToolRequest):
    "Parameters for the tools.psu.set_current_limit_mode endpoint"

    current_limit_mode: CurrentLimitMode


class PSUMode(str, Enum):
    """The operating mode of a PSU tool."""

    CONSTANT_CURRENT = "constant current"
    CONSTANT_VOLTAGE = "constant voltage"


class PSUState(BaseModel):
    """
    The state of a PSU tool

    Attributes:
        voltage (float): The output voltage in volts.
        current (float): The output current in amps.
        enabled (bool): True if the output of the PSU is enabled.
        tripped (bool): True if the PSU has tripped.
        mode (PSUMode): Operating mode of the tool.
    """

    voltage: float
    current: float
    enabled: bool
    tripped: bool
    mode: PSUMode


class Range(BaseModel):
    "An inclusive range."

    min: float
    max: float

    @model_validator(mode="after")
    def check_min_le_max(self) -> "Range":
        """Ensure that min <= max"""
        assert self.min <= self.max
        return self

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Range):
            raise NotImplementedError()
        return isclose(self.min, other.min) and isclose(self.max, other.max)


class CurrentCapabilities(Range):
    "The current capabilities of a power supply, all fields reported in Amps"

    limit_resolution: float
    min: Annotated[float, Field(le=0)]
    max: Annotated[float, Field(ge=0)]


class VoltageCapabilities(Range):
    "The voltage capabilities of a power supply, all fields reported in Volts"

    setpoint_resolution: Annotated[float, Field(gt=0)]
    sense_resolution: Annotated[float, Field(gt=0)]


class PSUSpec(BaseModel):
    "The specifications of a power supply"

    voltage: VoltageCapabilities
    current: CurrentCapabilities
