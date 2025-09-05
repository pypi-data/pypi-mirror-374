"""Environment variable definitions for ABV OpenTelemetry integration.

This module defines environment variables used to configure the ABV OpenTelemetry integration.
Each environment variable includes documentation on its purpose, expected values, and defaults.
"""

ABV_TRACING_ENVIRONMENT = "ABV_TRACING_ENVIRONMENT"
"""
.. envvar:: ABV_TRACING_ENVIRONMENT

The tracing environment. Can be any lowercase alphanumeric string with hyphens and underscores that does not start with 'abv'.

**Default value:** ``"default"``
"""

ABV_RELEASE = "ABV_RELEASE"
"""
.. envvar:: ABV_RELEASE

Release number/hash of the application to provide analytics grouped by release.
"""


ABV_PUBLIC_KEY = "ABV_PUBLIC_KEY"
"""
.. envvar:: ABV_PUBLIC_KEY

Public API key of ABV project
"""

ABV_SECRET_KEY = "ABV_SECRET_KEY"
"""
.. envvar:: ABV_SECRET_KEY

Secret API key of ABV project
"""

ABV_HOST = "ABV_HOST"
"""
.. envvar:: ABV_HOST

Host of ABV API. Can be set via `ABV_HOST` environment variable.

**Default value:** ``"https://app.abv.dev"``
"""

ABV_DEBUG = "ABV_DEBUG"
"""
.. envvar:: ABV_DEBUG

Enables debug mode for more verbose logging.

**Default value:** ``"False"``
"""

ABV_TRACING_ENABLED = "ABV_TRACING_ENABLED"
"""
.. envvar:: ABV_TRACING_ENABLED

Enables or disables the ABV client. If disabled, all observability calls to the backend will be no-ops. Default is True. Set to `False` to disable tracing.

**Default value:** ``"True"``
"""

ABV_MEDIA_UPLOAD_THREAD_COUNT = "ABV_MEDIA_UPLOAD_THREAD_COUNT"
"""
.. envvar:: ABV_MEDIA_UPLOAD_THREAD_COUNT 

Number of background threads to handle media uploads from trace ingestion.

**Default value:** ``1``
"""

ABV_FLUSH_AT = "ABV_FLUSH_AT"
"""
.. envvar:: ABV_FLUSH_AT

Max batch size until a new ingestion batch is sent to the API.
**Default value:** ``15``
"""

ABV_FLUSH_INTERVAL = "ABV_FLUSH_INTERVAL"
"""
.. envvar:: ABV_FLUSH_INTERVAL

Max delay in seconds until a new ingestion batch is sent to the API.
**Default value:** ``1``
"""

ABV_SAMPLE_RATE = "ABV_SAMPLE_RATE"
"""
.. envvar: ABV_SAMPLE_RATE

Float between 0 and 1 indicating the sample rate of traces to bet sent to ABV servers.

**Default value**: ``1.0``

"""
ABV_OBSERVE_DECORATOR_IO_CAPTURE_ENABLED = (
    "ABV_OBSERVE_DECORATOR_IO_CAPTURE_ENABLED"
)
"""
.. envvar: ABV_OBSERVE_DECORATOR_IO_CAPTURE_ENABLED

Default capture of function args, kwargs and return value when using the @observe decorator.

Having default IO capture enabled for observe decorated function may have a performance impact on your application
if large or deeply nested objects are attempted to be serialized. Set this value to `False` and use manual
input/output setting on your observation to avoid this.

**Default value**: ``True``
"""

ABV_MEDIA_UPLOAD_ENABLED = "ABV_MEDIA_UPLOAD_ENABLED"
"""
.. envvar: ABV_MEDIA_UPLOAD_ENABLED

Controls whether media detection and upload is attempted by the SDK.

**Default value**: ``True``
"""

ABV_TIMEOUT = "ABV_TIMEOUT"
"""
.. envvar: ABV_TIMEOUT

Controls the timeout for all API requests in seconds

**Default value**: ``5``
"""
