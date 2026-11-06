"""Compatibility shim: export_site lives in the markup-only ``app.pages`` package."""

from app.pages.site_export import export_site

__all__ = ["export_site"]
