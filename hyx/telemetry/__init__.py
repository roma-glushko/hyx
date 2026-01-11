"""
Telemetry instrumentation for Hyx components.

This package provides listeners that emit metrics for all Hyx fault tolerance
components using various backends.

Available backends:
    - OpenTelemetry: pip install hyx[otel]
    - StatsD: pip install hyx[statsd]
    - Prometheus: pip install hyx[prometheus]

Usage:
    # OpenTelemetry
    from hyx.telemetry.otel import register_listeners
    register_listeners()

    # StatsD
    from hyx.telemetry.statsd import register_listeners
    register_listeners()

    # Prometheus
    from hyx.telemetry.prometheus import register_listeners
    register_listeners()
"""
