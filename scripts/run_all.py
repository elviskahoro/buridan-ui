import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent

SCRIPT_SEQUENCE = [
    ["generate_registry.py"],
    ["generate_anatomy.py"],
    ["generate_markdown.py"],
    ["generate_search_index.py", "--no-reflex"],
    ["generate_sitemap.py"],
    ["generate_llms.py"],
    ["generate_preview_cards.py"],
]


def main() -> None:
    print("Initiating Buridan UI Pipeline Runner (with flags)...\n")

    for command_args in SCRIPT_SEQUENCE:
        script_name = command_args[0]
        script_path = SCRIPTS_DIR / script_name

        if not script_path.exists():
            print(f"❌ Pipeline Aborted: Script '{script_name}' could not be located.")
            sys.exit(1)

        print(f"Running: {' '.join(command_args)} ...")

        full_command = ["python", str(script_path), *command_args[1:]]

        result = subprocess.run(full_command, check=False)  # noqa: S603 - argv built from repo scripts

        if result.returncode != 0:
            print(f"\n❌ Pipeline Failed at execution point: '{script_name}'")
            sys.exit(1)

        print(f"Success: {script_name}\n" + "-" * 50)

    print("Pipeline compilation complete!")


if __name__ == "__main__":
    main()
