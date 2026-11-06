import os
import subprocess
from pathlib import Path

import questionary

DOCS_DIR = Path("docs")


MIN_DOC_PARTS = 2  # section directory + page name


def build_index() -> dict[str, list[str]]:
    """Builds:
    {
        "getting-started": ["introduction", "installation"],
        "components": ["button", "input"]
    }.
    """
    sections: dict[str, list[str]] = {}

    for file in DOCS_DIR.glob("**/*.md"):
        rel = file.relative_to(DOCS_DIR)
        parts = rel.with_suffix("").parts

        if len(parts) < MIN_DOC_PARTS:
            continue

        section = parts[0].replace("_", "-")
        page = parts[1].replace("_", "-")

        sections.setdefault(section, []).append(page)

    for pages in sections.values():
        pages.sort()

    return sections


def expand_sections(
    selected_sections: list[str],
    sections: dict[str, list[str]],
) -> list[str]:
    pages: list[str] = []
    for section in selected_sections:
        for page in sections.get(section, []):
            pages.append(f"{section}/{page}")
    return pages


def select_env() -> str | None:
    env = questionary.select(
        "Run mode:",
        choices=["dev", "prod"],
    ).ask()

    if env is None:
        return None

    return env


def select_mode() -> str | None:
    mode = questionary.select(
        "What do you want to select?",
        choices=[
            "pages",
            "sections",
            "section-pages",
        ],
    ).ask()

    if mode is None:
        return None

    return mode


def select_pages(sections: dict[str, list[str]]) -> list[str] | None:
    choices: list[str | questionary.Separator] = []

    for section, pages in sections.items():
        choices.append(questionary.Separator(f"[{section}]"))
        for page in pages:
            choices.append(f"{section}/{page}")

    result = questionary.checkbox(
        "Select pages:",
        choices=choices,
    ).ask()

    if not result:
        return None

    return result


def select_sections(sections: dict[str, list[str]]) -> list[str] | None:
    result = questionary.checkbox(
        "Select sections:",
        choices=list(sections.keys()),
    ).ask()

    if not result:
        return None

    return result


def select_pages_from_sections(
    selected_sections: list[str],
    sections: dict[str, list[str]],
) -> list[str] | None:
    choices: list[str | questionary.Separator] = []

    for section in selected_sections:
        pages = sections.get(section, [])

        choices.append(questionary.Separator(f"[{section}]"))

        for page in pages:
            choices.append(f"{section}/{page}")

    result = questionary.checkbox(
        "Select pages:",
        choices=choices,
    ).ask()

    if not result:
        return None

    return result


def run_reflex(env: str, pages: list[str] | None) -> str | None:
    """Runs Reflex and prints correct URLs ONLY after the actual port is known."""
    if env == "dev":
        os.environ["BURIDAN_DEV_MODE"] = "true"

        if pages:
            os.environ["BURIDAN_DEV_PAGES"] = ",".join(pages)
        else:
            os.environ.pop("BURIDAN_DEV_PAGES", None)
    else:
        os.environ.pop("BURIDAN_DEV_MODE", None)
        os.environ.pop("BURIDAN_DEV_PAGES", None)

    if env not in {"dev", "prod"}:
        msg = f"unexpected run mode: {env}"
        raise ValueError(msg)

    cmd = ["uv", "run", "reflex", "run", "--env", env]

    process = subprocess.Popen(  # noqa: S603 - fixed-choice args, env validated above
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    port: str | None = None

    if process.stdout is None:
        msg = "reflex process was started without stdout capture"
        raise RuntimeError(msg)
    for line in process.stdout:
        print(line, end="")

        # Detect actual runtime port from Reflex output
        if "App running at:" in line:
            try:
                port = line.split("http://localhost:")[1].split("/")[0]

                # Print correct clickable URLs ONLY when server is ready
                if pages:
                    base_url = f"http://localhost:{port}/docs"

                    print("\nLoading specified URLs:")
                    for page in pages:
                        print(f"{base_url}/{page}")

            except IndexError:
                # Line mentions localhost but not in the expected URL form.
                continue

    return port


def _select_pages(mode: str, sections: dict[str, list[str]]) -> list[str] | None:
    if mode == "pages":
        return select_pages(sections)
    if mode in {"sections", "section-pages"}:
        selected_sections = select_sections(sections)
        if selected_sections is None:
            return None
        if mode == "sections":
            return expand_sections(selected_sections, sections)
        return select_pages_from_sections(selected_sections, sections)
    return []


def main() -> None:
    sections = build_index()

    env = select_env()
    if env is None:
        print("Exiting")
        return

    # ---------------- FAST PATH: PROD ----------------
    if env == "prod":
        print("Launching full site (prod mode)...")
        run_reflex(env, pages=None)
        return

    # ---------------- DEV FLOW ----------------
    mode = select_mode()
    if mode is None:
        print("Exiting")
        return

    selected_pages = _select_pages(mode, sections)
    if selected_pages is None:
        print("Exiting")
        return

    confirm = questionary.confirm(
        f"Run reflex in {env} with {len(selected_pages)} pages?",
    ).ask()

    if not confirm:
        print("Cancelled")
        return

    run_reflex(env, selected_pages)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting")
