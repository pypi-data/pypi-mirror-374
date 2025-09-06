# doc-tracker

Track and merge multiple documentation files into a single output file.

## Install

```bash
pip install doc-tracker
```

## Commands

- `doc-tracker init <folder>`: Create a project folder with `config.yaml` and `master-doc.md`.
- `doc-tracker watch`: Aggregate once and then watch for changes in the current folder.

> Note: All generated files stay inside the init folder. No files are created elsewhere.

## Quick Start

```bash
# 1) Initialize a project folder
doc-tracker init mydocs

# 2) Add your documents (use absolute paths) to mydocs/config.yaml
#    Example config:
#    output_file: master-doc.md
#    tracked_documents:
#      - /absolute/path/to/README.md
#      - /absolute/path/to/docs/*.md

# 3) Run the watcher inside the folder
cd mydocs
doc-tracker watch
```

## Output Format

- Each document starts with a header box containing the path relative to the project folder, with `@` and two spaces on both sides. Example:

```
╭──────────────╮
│  @docs/a.md  │
╰──────────────╯
```

## Notes

- `config.yaml` and the output file (e.g., `master-doc.md`) must be inside the project folder.
- Use absolute file paths in `tracked_documents`. The display in the merged output stays relative to the project folder.
