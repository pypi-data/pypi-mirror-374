class TelemetryError(Exception):
    """Base exception for the telemetry client."""
    pass

class FeedVersionError(TelemetryError):
    """Raised when the telemetry feed version is incompatible."""
    pass
