# QML Formatter Hook

A pre-commit hook for formatting QML files using `qmlformat` tool.

## Usage

Add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/baiyao105/qml-formatter
    rev: v1
    hooks:
      - id: qml-format
```
