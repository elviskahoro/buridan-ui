import os
import inspect
import importlib

from typing import Callable, Dict, List
from buridan_ui.config import BASE_PANTRY_PATH, BASE_CHART_PATH
from buridan_ui.ui.organisms.grid import responsive_grid
from buridan_ui.wrappers.component.wrapper import component_wrapper


# Define a unified configuration system
class ExportConfig:
    def __init__(self):
        # Component configurations
        self.COMPONENTS = {
            "sidebars": {"versions": range(1, 2), "func_prefix": "sidebar"},
            "accordions": {"versions": range(1, 2), "func_prefix": "accordion"},
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
            "area": {
                "versions": range(1, 9),
                "func_prefix": "areachart",
                "flexgen": "https://reflex.build/gen/85caad0f-95d1-4180-b4eb-fc72edafdc9a/",
            },
            "bar": {"versions": range(1, 11), "func_prefix": "barchart"},
            "line": {"versions": range(1, 9), "func_prefix": "linechart"},
            "pie": {"versions": range(1, 7), "func_prefix": "piechart"},
            "radar": {"versions": range(1, 7), "func_prefix": "radar"},
            "scatter": {"versions": [1], "func_prefix": "scatterchart"},
            "doughnut": {"versions": range(1, 3), "func_prefix": "doughnutchart"},
            "sunburst": {"versions": [1], "func_prefix": "sunburst"},
            "bump": {"versions": [1], "func_prefix": "bump"},
            "chord": {"versions": [1], "func_prefix": "chord"},
        }

        # Grid configurations
        self.GRID_CONFIGS = {
            "animations": {"lg": 2, "gap": 8},
            "backgrounds": {"lg": 2},
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

        # Check if the function name starts with 'sunburst' or 'bump'
        if not (
            func.__name__.startswith("sunburst") or func.__name__.startswith("bump")
        ):
            # Only read the file if the name doesn't start with 'sunburst' or 'bump'
            with open("buridan_ui/charts/style.py") as file:
                source += file.read()
                source += "\n"

        source += inspect.getsource(func)
        return source


class ExportFactory:
    """Factory class for creating exports"""

    @staticmethod
    def create_pantry_export(
        directory: str,
        version: int,
        func_prefix: str,
        flexgen_url: str = "https://reflex.build/gen/85caad0f-95d1-4180-b4eb-fc72edafdc9a/",
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
                flexgen_url,
            ]

        return export

    @staticmethod
    def create_chart_export(
        directory: str,
        version: int,
        func_prefix: str,
        flexgen_url: str = "",
    ) -> Callable:
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
            return [chart_func(), SourceRetriever.chart_source(chart_func), flexgen_url]

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
