# Runtime Recovery Playbook

## Goal
Recover runtime health safely without hanging the console, creating false alarms, or introducing broad regressions.

## Safe operating rules
Always follow these rules during runtime recovery work:

- use short, scoped commands
- do not run foreground loops unless explicitly intended
- inspect first, patch second
- avoid broad mass-replace operations
- use compile or syntax checks before restarts
- verify recovery with one monitor run and one proof read

## Standard preflight gate

### For Python files
Run:

```bash
python3 -m py_compile <file>