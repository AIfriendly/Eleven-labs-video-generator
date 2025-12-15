# Eleven Labs AI Video Generator

A terminal-based tool to generate AI videos using Eleven Labs and Gemini APIs.

## Features

- Automated video generation from text prompts
- AI-powered voiceover using Eleven Labs TTS
- Intelligent image generation with Gemini
- Real-time progress monitoring with Rich UI
- Configurable via environment variables

## Prerequisites

- **Python 3.9+** required
- **Eleven Labs API key** - [Get one here](https://elevenlabs.io/)
- **Gemini API key** - [Get one here](https://ai.google.dev/)

## Installation

First, install `uv` (recommended package manager):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then, install the project dependencies:

```bash
uv pip install -e ".[dev]"
```

Alternatively, with pip:

```bash
pip install -e ".[dev]"
```

## Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` and add your API keys:
   ```
   ELEVEN_LABS_API_KEY=your_key_here
   GEMINI_API_KEY=your_key_here
   ```

## Usage

```bash
eleven-video --help
```

### Available Options

| Option | Short | Description |
|--------|-------|-------------|
| `--prompt` | `-p` | Text prompt to generate video from |
| `--voice` | `-v` | Voice ID to use |
| `--api-key` | `-k` | Eleven Labs API Key |
| `--gemini-key` | `-g` | Gemini API Key |
| `--output` | `-o` | Output file path |
| `--version` | | Show version and exit |

## Development

Run tests:
```bash
uv run pytest tests/ -v
```

Run linting:
```bash
uv run ruff check .
uv run black --check .
```

## License

MIT License - see [LICENSE](LICENSE) for details.