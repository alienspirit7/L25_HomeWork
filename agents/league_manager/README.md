# League Manager (Modular Version)

This is the restructured League Manager following Section 11 architecture pattern.

## Structure

- **main.py**: Entry point, initialization, server startup
- **handlers.py**: Message handling logic (registration, match results, queries)
- **scheduler.py**: Round management, announcements, completions
- **requirements.txt**: Python dependencies

## Key Improvements

✅ **SDK Integration**: Uses `league_sdk` for configuration, logging, and utilities
✅ **Modular Design**: Separated concerns into logical modules
✅ **Type Safety**: Leverages SDK dataclasses for configuration
✅ **Structured Logging**: JSONL logging via SDK
✅ **Maintainability**: Clear separation of responsibilities

## Usage

```bash
# Install dependencies
cd agents/league_manager
pip install -r requirements.txt
pip install -e ../../SHARED  # Install league_sdk

# Run
python main.py --league-id league_2025_even_odd
```

## Migration from src/league_manager.py

The monolithic `src/league_manager.py` (719 lines) has been split into:

1. **main.py** (~200 lines): Core orchestration
2. **handlers.py** (~280 lines): All message handlers
3. **scheduler.py** (~220 lines): Scheduling logic

This follows the recommended pattern from Section 11.4.1.
