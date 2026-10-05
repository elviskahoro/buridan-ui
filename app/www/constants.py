from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import reflex as rx


@dataclass
class DocDataStruct:
    """The data structure for the generated doc page"""

    url: str
    description: str
    component: List[rx.Component]
    table_of_content: List[Dict]


# --- Docs Path Constants ---
_PROJECT_ROOT = Path(__file__).resolve().parents[2]

DOCS_BASE_DIR = _PROJECT_ROOT / "docs"
DOCS_LIBRARY_ROOT = str(_PROJECT_ROOT / "app" / "www" / "library")
COMPONENTS_ROOT = "components/ui"
