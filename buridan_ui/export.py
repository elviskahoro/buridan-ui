import os
import inspect
import importlib

from typing import Callable, Dict, List
from buridan_ui.wrappers.component.wrapper import component_wrapper
from buridan_ui.config import BASE_PANTRY_PATH, BASE_CHART_PATH
from buridan_ui.ui.organisms.grid import responsive_grid


# Define a unified configuration system
class ExportConfig:
    def __init__(self):
        # Component configurations
        self.COMPONENTS = {
            "animations": {"versions": range(1, 7), "func_prefix": "animation"},
            "backgrounds": {"versions": range(1, 5), "func_prefix": "background"},
            "cards": {"versions": range(1, 4), "func_prefix": "card"},
            "faq": {"versions": [1], "func_prefix": "faq"},
            "featured": {"versions": range(1, 3), "func_prefix": "featured"},
            "footers": {"versions": range(1, 3), "func_prefix": "footer"},
            "forms": {"versions": range(1, 4), "func_prefix": "forms"},
            "inputs": {"versions": range(1, 5), "func_prefix": "inputs"},
            "lists": {"versions": [1], "func_prefix": "lists"},
            "logins": {"versions": range(1, 3), "func_prefix": "logins"},
            "menus": {"versions": [1], "func_prefix": "menus"},
            "onboardings": {"versions": [1], "func_prefix": "onboardings"},
            "payments": {"versions": [1], "func_prefix": "payments"},
            "popups": {"versions": range(1, 3), "func_prefix": "popups"},
            "pricing": {"versions": range(1, 3), "func_prefix": "pricing"},
            "prompts": {"versions": range(1, 3), "func_prefix": "prompt"},
            "subscribe": {"versions": range(1, 3), "func_prefix": "subscribe"},
            "tables": {"versions": range(1, 5), "func_prefix": "tables"},
            "timeline": {"versions": [1], "func_prefix": "timeline"},
        }

        # Chart configurations
        self.CHARTS = {
            "bar": {"versions": [1, 2, 3, 4, 5, 6, 7], "func_prefix": "barchart"},
            "area": {"versions": range(1, 8), "func_prefix": "areachart"},
            "line": {"versions": range(1, 8), "func_prefix": "linechart"},
            "pie": {"versions": range(1, 7), "func_prefix": "piechart"},
            "radar": {"versions": range(1, 7), "func_prefix": "radar"},
        }

        # Grid configurations
        self.GRID_CONFIGS = {
            "animations": {"lg": 2, "gap": 8},
            "backgrounds": {"lg": 2},
            # Add other custom grid configs as needed
        }


# Create a singleton config instance
config = ExportConfig()


class SourceRetriever:
    """Class to handle different source code retrieval strategies"""

    @staticmethod
    def pantry_source(directory: str, filename: str) -> str:
        """Get source for pantry components."""
        with open(os.path.join("buridan_ui", "pantry", directory, filename)) as file:
            return file.read()

    @staticmethod
    def chart_source(func: Callable) -> str:
        """Get source for chart components including style.py."""
        source: str = ""
        with open("buridan_ui/charts/style.py") as file:
            source += file.read()
            source += "\n"
            source += inspect.getsource(func)
        return source


class ExportFactory:
    """Factory class for creating exports"""

    @staticmethod
    def create_pantry_export(
        directory: str, version: int, func_prefix: str
    ) -> Callable:
        """Create an export function for a pantry component."""
        # Import the component dynamically
        component_func = ExportFactory._import_component(
            base_module="buridan_ui.pantry",
            directory=directory,
            version=version,
            func_prefix=func_prefix,
        )

        @component_wrapper(f"{BASE_PANTRY_PATH}{directory}/v{version}.py")
        def export():
            return [
                component_func(),
                SourceRetriever.pantry_source(directory, f"v{version}.py"),
            ]

        return export

    @staticmethod
    def create_chart_export(directory: str, version: int, func_prefix: str) -> Callable:
        """Create an export function for a chart component."""
        # Import the chart component dynamically
        chart_func = ExportFactory._import_component(
            base_module="buridan_ui.charts",
            directory=directory,
            version=version,
            func_prefix=func_prefix,
        )

        @component_wrapper(f"{BASE_CHART_PATH}{directory}/v{version}.py")
        def export():
            return [chart_func(), SourceRetriever.chart_source(chart_func)]

        return export

    @staticmethod
    def _import_component(
        base_module: str, directory: str, version: int, func_prefix: str
    ) -> Callable:
        """Dynamically import a component function."""
        module_path = f"{base_module}.{directory}.v{version}"
        function_name = f"{func_prefix}_v{version}"

        try:
            module = importlib.import_module(module_path)
            return getattr(module, function_name)
        except (ImportError, AttributeError) as e:
            raise ImportError(
                f"Failed to import {function_name} from {module_path}: {e}"
            )

    @staticmethod
    def import_page(module_path: str, func_name: str) -> Callable:
        """Import a page function directly."""
        try:
            module = importlib.import_module(module_path)
            return getattr(module, func_name)
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Failed to import {func_name} from {module_path}: {e}")


def generate_pantry_exports() -> Dict[str, List]:
    """Generate all pantry component exports dynamically."""
    exports = {}

    for directory, details in config.COMPONENTS.items():
        versions = details["versions"]
        func_prefix = details["func_prefix"]
        component_exports = []
        export_items = []

        for version in versions:
            export_func = ExportFactory.create_pantry_export(
                directory, version, func_prefix
            )
            export_items.append(export_func())

        # Get any custom grid config for this component type
        grid_config = config.GRID_CONFIGS.get(directory, {})

        # Use responsive_grid to organize the exports
        component_exports.append(responsive_grid(*export_items, **grid_config))
        exports[directory] = component_exports

    return exports


def generate_chart_exports() -> Dict[str, List]:
    """Generate all chart exports dynamically."""
    exports = {}

    for chart_type, details in config.CHARTS.items():
        versions = details["versions"]
        func_prefix = details["func_prefix"]
        chart_exports = []
        export_items = []

        for version in versions:
            export_func = ExportFactory.create_chart_export(
                chart_type, version, func_prefix
            )
            export_items.append(export_func())

        # Get any custom grid config for this chart type
        grid_config = config.GRID_CONFIGS.get(chart_type, {})

        # Use responsive_grid to organize the exports
        chart_exports.append(responsive_grid(*export_items, **grid_config))
        exports[chart_type] = chart_exports

    return exports


# Generate the exports
pantry_exports_config = generate_pantry_exports()
charts_exports_config = generate_chart_exports()
