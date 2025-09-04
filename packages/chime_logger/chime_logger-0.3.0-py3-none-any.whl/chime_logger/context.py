"""Dynamic logging context for CHIME project."""

import logging
from logging import Logger
from typing import Literal

from pydantic import BaseModel, validator


class DynamicLoggerAdapter(logging.LoggerAdapter):
    """Dynamic LoggerAdapter that updates context from a Pydantic model.

    Attributes:
        context_obj: A Pydantic model instance providing dynamic context data.
    """

    def __init__(self, logger: Logger, context_obj):
        """Initialise the DynamicLoggerAdapter.

        Args:
            logger (Logger): The base logger to adapt.
            context_obj (LoggerContext): A Pydantic model instance providing dynamic context data.
        """
        self.context_obj = context_obj
        super().__init__(logger, {})

    def process(self, msg, kwargs):
        """Process the logging message and keyword arguments.

        Args:
            msg ([TODO:parameter]): [TODO:description]
            kwargs ([TODO:parameter]): [TODO:description]

        Returns:
            [TODO:return]
        """
        # Get fresh context data each time
        return msg, {**kwargs, "extra": self.context_obj.dict()}


class LoggerContext(BaseModel):
    """Contains dynamic context information for logging.

    Attributes:
        resource_name: Name of the resource being processed.
        resource_type: Resource type, e.g., 'event', 'n2_acquisition', 'raw_adc'.
        pipeline: Name of the processing pipeline.
        site: Site where the processing is occurring, e.g., 'chime', 'kko', 'gbo', 'hco'.
    """

    resource_name: str
    resource_type: Literal["event", "n2_acquisition", "raw_adc"]
    pipeline: Literal[
        "baseband-conversion",
        "datatrail-deletion",
        "datatrail-registration",
        "datatrail-replication",
        "l4-trigger",
    ]
    site: Literal["chime", "kko", "gbo", "hco"]

    @validator("resource_name", "resource_type", pre=True)
    def _normalise_string_field(cls, v, field):
        """Normalise string fields to lowercase.

        Args:
            v: Value to validate.
            field: Field being validated.

        Returns:
            Validated and normalised value.

        Raises:
            ValueError: If the value is not a string.
        """
        if isinstance(v, str):
            return v.lower()
        raise ValueError(f"{field.name} must be a string")

    class Config:
        """Configuration for the LoggerContext model.

        Attributes:
            anystr_strip_whitespace:
            min_anystr_length:
            validate_assignment:
        """

        anystr_strip_whitespace = True
        min_anystr_length = 1
        validate_assignment = True
