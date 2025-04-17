# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build Commands
```bash
# Install dependencies
pip install -r requirements.txt
# OR with conda
conda env create -f environment.yml
conda activate myenv

# Run the application
python main.py
```

## Code Style Guidelines
- **Imports**: Follow PEP 8 order (stdlib → third-party → local)
- **Classes**: PascalCase with descriptive names
- **Methods/Variables**: snake_case
- **Private attributes**: Use leading underscore (_variable_name)
- **Type annotations**: Use for all function parameters and returns
- **Documentation**: Google-style docstrings for classes and methods
- **Error handling**: Raise explicit exceptions with descriptive messages
- **Patterns**: Singleton pattern for managers (MaterialManager, DampingManager)
- **Validation**: Parameter validation before object creation

When making changes, follow existing patterns in related files and maintain consistent style with surrounding code.