def doc_page_strings(url: str) -> tuple[str, str, str]:
    """Return (display title, page title, social card filename) for a docs url."""
    slug = url.split("/")[-1]
    title_s = slug.replace("-", " ").title()
    return title_s, f"{title_s} - buridan/ui", f"{slug}.webp"
