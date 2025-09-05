"""Span attribute management for ABV OpenTelemetry integration.

This module defines constants and functions for managing OpenTelemetry span attributes
used by ABV. It provides a structured approach to creating and manipulating
attributes for different span types (trace, span, generation) while ensuring consistency.

The module includes:
- Attribute name constants organized by category
- Functions to create attribute dictionaries for different entity types
- Utilities for serializing and processing attribute values
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from abv._client.constants import (
    ObservationTypeGenerationLike,
    ObservationTypeSpanLike,
)

from abv._utils.serializer import EventSerializer
from abv.model import PromptClient
from abv.types import MapValue, SpanLevel


class ABVOtelSpanAttributes:
    # ABV-Trace attributes
    TRACE_NAME = "abv.trace.name"
    TRACE_USER_ID = "user.id"
    TRACE_SESSION_ID = "session.id"
    TRACE_TAGS = "abv.trace.tags"
    TRACE_PUBLIC = "abv.trace.public"
    TRACE_METADATA = "abv.trace.metadata"
    TRACE_INPUT = "abv.trace.input"
    TRACE_OUTPUT = "abv.trace.output"

    # ABV-observation attributes
    OBSERVATION_TYPE = "abv.observation.type"
    OBSERVATION_METADATA = "abv.observation.metadata"
    OBSERVATION_LEVEL = "abv.observation.level"
    OBSERVATION_STATUS_MESSAGE = "abv.observation.status_message"
    OBSERVATION_INPUT = "abv.observation.input"
    OBSERVATION_OUTPUT = "abv.observation.output"

    # ABV-observation of type Generation attributes
    OBSERVATION_COMPLETION_START_TIME = "abv.observation.completion_start_time"
    OBSERVATION_MODEL = "abv.observation.model.name"
    OBSERVATION_MODEL_PARAMETERS = "abv.observation.model.parameters"
    OBSERVATION_USAGE_DETAILS = "abv.observation.usage_details"
    OBSERVATION_COST_DETAILS = "abv.observation.cost_details"
    OBSERVATION_PROMPT_NAME = "abv.observation.prompt.name"
    OBSERVATION_PROMPT_VERSION = "abv.observation.prompt.version"

    # General
    ENVIRONMENT = "abv.environment"
    RELEASE = "abv.release"
    VERSION = "abv.version"

    # Internal
    AS_ROOT = "abv.internal.as_root"


def create_trace_attributes(
    *,
    name: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    version: Optional[str] = None,
    release: Optional[str] = None,
    input: Optional[Any] = None,
    output: Optional[Any] = None,
    metadata: Optional[Any] = None,
    tags: Optional[List[str]] = None,
    public: Optional[bool] = None,
) -> dict:
    attributes = {
        ABVOtelSpanAttributes.TRACE_NAME: name,
        ABVOtelSpanAttributes.TRACE_USER_ID: user_id,
        ABVOtelSpanAttributes.TRACE_SESSION_ID: session_id,
        ABVOtelSpanAttributes.VERSION: version,
        ABVOtelSpanAttributes.RELEASE: release,
        ABVOtelSpanAttributes.TRACE_INPUT: _serialize(input),
        ABVOtelSpanAttributes.TRACE_OUTPUT: _serialize(output),
        ABVOtelSpanAttributes.TRACE_TAGS: tags,
        ABVOtelSpanAttributes.TRACE_PUBLIC: public,
        **_flatten_and_serialize_metadata(metadata, "trace"),
    }

    return {k: v for k, v in attributes.items() if v is not None}


def create_span_attributes(
    *,
    metadata: Optional[Any] = None,
    input: Optional[Any] = None,
    output: Optional[Any] = None,
    level: Optional[SpanLevel] = None,
    status_message: Optional[str] = None,
    version: Optional[str] = None,
    observation_type: Optional[
        Union[ObservationTypeSpanLike, Literal["event"]]
    ] = "span",
) -> dict:
    attributes = {
        ABVOtelSpanAttributes.OBSERVATION_TYPE: observation_type,
        ABVOtelSpanAttributes.OBSERVATION_LEVEL: level,
        ABVOtelSpanAttributes.OBSERVATION_STATUS_MESSAGE: status_message,
        ABVOtelSpanAttributes.VERSION: version,
        ABVOtelSpanAttributes.OBSERVATION_INPUT: _serialize(input),
        ABVOtelSpanAttributes.OBSERVATION_OUTPUT: _serialize(output),
        **_flatten_and_serialize_metadata(metadata, "observation"),
    }

    return {k: v for k, v in attributes.items() if v is not None}


def create_generation_attributes(
    *,
    name: Optional[str] = None,
    completion_start_time: Optional[datetime] = None,
    metadata: Optional[Any] = None,
    level: Optional[SpanLevel] = None,
    status_message: Optional[str] = None,
    version: Optional[str] = None,
    model: Optional[str] = None,
    model_parameters: Optional[Dict[str, MapValue]] = None,
    input: Optional[Any] = None,
    output: Optional[Any] = None,
    usage_details: Optional[Dict[str, int]] = None,
    cost_details: Optional[Dict[str, float]] = None,
    prompt: Optional[PromptClient] = None,
    observation_type: Optional[ObservationTypeGenerationLike] = "generation",
) -> dict:
    attributes = {
        ABVOtelSpanAttributes.OBSERVATION_TYPE: observation_type,
        ABVOtelSpanAttributes.OBSERVATION_LEVEL: level,
        ABVOtelSpanAttributes.OBSERVATION_STATUS_MESSAGE: status_message,
        ABVOtelSpanAttributes.VERSION: version,
        ABVOtelSpanAttributes.OBSERVATION_INPUT: _serialize(input),
        ABVOtelSpanAttributes.OBSERVATION_OUTPUT: _serialize(output),
        ABVOtelSpanAttributes.OBSERVATION_MODEL: model,
        ABVOtelSpanAttributes.OBSERVATION_PROMPT_NAME: prompt.name
        if prompt and not prompt.is_fallback
        else None,
        ABVOtelSpanAttributes.OBSERVATION_PROMPT_VERSION: prompt.version
        if prompt and not prompt.is_fallback
        else None,
        ABVOtelSpanAttributes.OBSERVATION_USAGE_DETAILS: _serialize(usage_details),
        ABVOtelSpanAttributes.OBSERVATION_COST_DETAILS: _serialize(cost_details),
        ABVOtelSpanAttributes.OBSERVATION_COMPLETION_START_TIME: _serialize(
            completion_start_time
        ),
        ABVOtelSpanAttributes.OBSERVATION_MODEL_PARAMETERS: _serialize(
            model_parameters
        ),
        **_flatten_and_serialize_metadata(metadata, "observation"),
    }

    return {k: v for k, v in attributes.items() if v is not None}


def _serialize(obj: Any) -> Optional[str]:
    if obj is None or isinstance(obj, str):
        return obj

    return json.dumps(obj, cls=EventSerializer)


def _flatten_and_serialize_metadata(
    metadata: Any, type: Literal["observation", "trace"]
) -> dict:
    prefix = (
        ABVOtelSpanAttributes.OBSERVATION_METADATA
        if type == "observation"
        else ABVOtelSpanAttributes.TRACE_METADATA
    )

    metadata_attributes: Dict[str, Union[str, int, None]] = {}

    if not isinstance(metadata, dict):
        metadata_attributes[prefix] = _serialize(metadata)
    else:
        for key, value in metadata.items():
            metadata_attributes[f"{prefix}.{key}"] = (
                value
                if isinstance(value, str) or isinstance(value, int)
                else _serialize(value)
            )

    return metadata_attributes
