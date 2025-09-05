"""
TLPyTools - A set of tools for building models at the TransLink Forecasting Team
"""

__version__ = "0.1.7"

"""
TLPyTools - A set of tools for building models at the TransLink Forecasting Team
"""

__version__ = "0.1.7"

# Core modules that should always be available (minimal dependencies)
from . import log

__all__ = ["log"]

# Optional modules - try to import but continue if dependencies are missing
_optional_modules = {
    "config": "config module (requires yaml and other dependencies)",
    "adls_server": "adls_server module (requires azure dependencies)",
    "data": "data module (may require geopandas for spatial operations)",
    "data_store": "data_store module (may require geopandas for spatial operations)",
    "sql_server": "sql_server module (requires pyodbc and may require geopandas)",
}

for module_name, description in _optional_modules.items():
    try:
        module = __import__(f"{__name__}.{module_name}", fromlist=[module_name])
        globals()[module_name] = module
        __all__.append(module_name)
    except ImportError as e:
        # Create a placeholder that provides helpful error messages
        class MissingModulePlaceholder:
            def __init__(self, module_name, description, import_error):
                self._module_name = module_name
                self._description = description
                self._import_error = import_error

            def __getattr__(self, name):
                raise ImportError(
                    f"Module '{self._module_name}' is not available: {self._description}. "
                    f"Original error: {self._import_error}"
                )

        globals()[module_name] = MissingModulePlaceholder(
            module_name, description, str(e)
        )
        # Still add to __all__ so users can see what's supposed to be available
        __all__.append(module_name)

# Clean up temporary variables
del _optional_modules

# Optional namespaces that require additional dependencies
try:
    from . import orca

    __all__.append("orca")
except ImportError as e:
    # Create a placeholder for the orca namespace
    class MissingOrcaPlaceholder:
        def __getattr__(self, name):
            raise ImportError(
                "ORCA functionality requires additional dependencies. "
                "Install with: pip install tlpytools[orca]"
            )

    orca = MissingOrcaPlaceholder()
    __all__.append("orca")
