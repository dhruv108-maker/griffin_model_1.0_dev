import os

# -----------------------------
# Configuration
# -----------------------------
INPUT_FOLDER = r"backend"
OUTPUT_MD = "folder_structure.md"

IGNORE_DIRS = {
    "__pycache__",
    ".git",
    ".idea",
    ".vscode",
    "node_modules",
    ".venv",
    "venv",
    "env",
    "build",
    "dist"
}

IGNORE_FILES = {
    ".DS_Store"
}


def generate_tree(path, prefix=""):
    entries = sorted(
        os.listdir(path),
        key=lambda x: (
            not os.path.isdir(os.path.join(path, x)),
            x.lower()
        )
    )

    entries = [
        e for e in entries
        if e not in IGNORE_DIRS
        and e not in IGNORE_FILES
    ]

    lines = []

    for i, entry in enumerate(entries):
        full_path = os.path.join(path, entry)

        connector = "└── " if i == len(entries) - 1 else "├── "
        lines.append(prefix + connector + entry)

        # Recurse only if directory
        if os.path.isdir(full_path):
            extension = "    " if i == len(entries) - 1 else "│   "
            lines.extend(generate_tree(full_path, prefix + extension))

    return lines


def main():
    root_name = os.path.basename(os.path.abspath(INPUT_FOLDER))

    tree = [root_name]
    tree.extend(generate_tree(INPUT_FOLDER))

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("# Project Structure\n\n")
        f.write("```text\n")
        f.write("\n".join(tree))
        f.write("\n```\n")

    print(f"Saved to {OUTPUT_MD}")


if __name__ == "__main__":
    main()