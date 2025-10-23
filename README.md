# QML Formatter Hook

A pre-commit hook for formatting QML files using `qmlformat` tool.

## Usage

Add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/your-username/qml-formatter-hook
    rev: v1.0.0
    hooks:
      - id: qml-format
```
