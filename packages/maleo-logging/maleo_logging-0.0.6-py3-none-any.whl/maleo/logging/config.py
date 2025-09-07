from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Optional, Self
from maleo.types.base.dict import OptionalStringToStringDict
from maleo.types.base.string import OptionalString
from .enums import Level
from .google import GoogleCloudLogging


class Config(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    dir: str = Field(..., description="Log's directory")
    level: Level = Field(Level.INFO, description="Log's level")
    google_cloud_logging: Optional[GoogleCloudLogging] = Field(
        default_factory=GoogleCloudLogging, description="Google cloud logging"
    )
    labels: OptionalStringToStringDict = Field(
        None, description="Log labels. (Optional)"
    )
    aggregate_file_name: OptionalString = Field(
        None, description="Log aggregate file name"
    )
    individual_log: bool = Field(True, description="Whether to have individual log")

    @model_validator(mode="after")
    def validate_aggregate_file_name(self) -> Self:
        if isinstance(self.aggregate_file_name, str):
            if not self.aggregate_file_name.endswith(".log"):
                self.aggregate_file_name += ".log"

        return self
