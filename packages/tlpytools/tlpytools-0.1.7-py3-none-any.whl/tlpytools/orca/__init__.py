"""
ORCA Model Orchestration Module

This module provides tools for orchestrating ORCA model runs, including
initialization, execution, and data synchronization.

This module is optional and requires additional dependencies.
Install with: pip install tlpytools[orca]
"""

# Optional imports with graceful fallbacks
try:
    from .orchestrator import OrcaOrchestrator, main

    __all__ = ["OrcaOrchestrator", "main"]
except ImportError as e:
    import warnings

    warnings.warn(
        f"ORCA orchestrator functionality not available: {e}. "
        "Install with: pip install tlpytools[orca]",
        ImportWarning,
    )

    class _MissingOrcaPlaceholder:
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "ORCA orchestrator functionality requires additional dependencies. "
                "Install with: pip install tlpytools[orca]"
            )

    def _missing_main(*args, **kwargs):
        raise ImportError(
            "ORCA orchestrator functionality requires additional dependencies. "
            "Install with: pip install tlpytools[orca]"
        )

    OrcaOrchestrator = _MissingOrcaPlaceholder
    main = _missing_main
    __all__ = ["OrcaOrchestrator", "main"]
