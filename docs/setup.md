# Setup Guide

## Requirements

- Python 3.11+
- `pip` or `uv`

## Installation

```bash
# Clone the repo (or copy the template)
cd uefi-<subject-name>

# Install with pip
pip install -e .

# Or with uv (recommended)
uv pip install -e .

# For subjects requiring symbolic math
pip install -e ".[math]"

# For subjects requiring image handling
pip install -e ".[vision]"
```

## Running the server

The server communicates via **stdio**, which is the standard MCP transport for Claude Desktop and Claude Code.

```bash
python -m src.server
```

Or using the installed script:

```bash
uefi-mcp
```

## Connecting to Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "uefi-<subject>": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/uefi-<subject>"
    }
  }
}
```

## Connecting to Claude Code

```bash
claude mcp add uefi-<subject> python -m src.server --cwd /path/to/uefi-<subject>
```

## Verifying the setup

Once connected, ask Claude: *"What tools does the subject MCP expose?"*  
It should list: `get_syllabus`, `get_bibliography`, `get_past_exams`, `search_content`, `get_notes`, `explain_concept`, `get_topic_outline`, `generate_study_plan`, `get_exercises`, `solve_exercise`, `generate_exercise`, `generate_flashcards`.
