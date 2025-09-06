# injectenv

A simple and flexible command-line tool for injecting environment variables into spawned processes.

## Features

- **Multiple sources**: Load variables from command-line flags, `.env` files, and profiles
- **Flexible precedence**: Customize which sources override others with `--order`
- **Profile support**: Load environment-specific configs with `.env.<profile>` files
- **JSON output**: Export merged environment as JSON for debugging or integration
- **Shell support**: Run commands through shell or directly
- **Dry-run mode**: Preview environment variables without executing commands

## Installation

```bash
pip install injectenv
```

## Quick Start

```bash
# Set variables and run a command
injectenv -e NODE_ENV=production -e PORT=3000 -- node server.js

# Load from .env file and override specific variables
injectenv -f .env -e DEBUG=true -- python app.py

# Use profiles for different environments
injectenv --profile dev --profile local -- npm start

# Preview the merged environment
injectenv -f .env --profile production --print-env
```

## Usage

```
injectenv [OPTIONS] [--] COMMAND [ARGS...]
```

### Environment Sources

- **`-e, --env KEY=VAL`**: Set individual variables (repeatable)
- **`-f, --file FILE`**: Load from `.env` file (repeatable)
- **`--profile NAME`**: Load from `.env.NAME` file (repeatable)

By default, `injectenv` also loads `./.env` if it exists.

### Precedence Control

- **`--order SOURCES`**: Comma-separated list defining precedence (default: `system,file,flags`)
  - `system`: Current environment variables
  - `file`: Variables from `.env` files and profiles
  - `flags`: Variables from `-e/--env` flags

### Additional Options

- **`--unset KEY`**: Remove variables before spawning (repeatable)
- **`--print-env`**: Print merged environment before running command
- **`--json`**: Output environment as JSON and exit (no command execution)
- **`-s, --shell`**: Run command through shell
- **`--no-inherit-stdio`**: Stream output instead of inheriting stdio

## Examples

### Basic Usage

```bash
# Simple variable injection
injectenv -e API_KEY=secret123 -- curl -H "Authorization: $API_KEY" api.example.com

# Multiple variables
injectenv -e NODE_ENV=production -e PORT=8080 -e DEBUG=false -- node app.js
```

### File-Based Configuration

```bash
# Load from specific file
injectenv -f config/production.env -- python manage.py runserver

# Multiple files (later files override earlier ones)
injectenv -f .env -f .env.local -- npm run build
```

### Environment Profiles

```bash
# Development setup
injectenv --profile dev -- python app.py

# Multiple profiles (development + local overrides)
injectenv --profile dev --profile local -- npm start

# Production with custom overrides
injectenv --profile prod -e DEBUG=true -- ./deploy.sh
```

### Precedence Examples

```bash
# Default: system < file < flags
injectenv -f .env -e NODE_ENV=development -- node app.js

# Custom order: flags < system < file
injectenv --order flags,system,file -f .env -e NODE_ENV=development -- node app.js

# Files override everything
injectenv --order system,flags,file -f .env -e NODE_ENV=development -- node app.js
```

### Debugging and Inspection

```bash
# Preview environment without running command
injectenv -f .env --profile production --print-env

# Export as JSON for processing
injectenv -f .env --profile dev --json > current-env.json

# Remove sensitive variables
injectenv -f .env --unset SECRET_KEY --unset API_TOKEN -- python app.py
```

## File Format

Environment files use the standard `.env` format:

```bash
# .env
NODE_ENV=development
PORT=3000
DEBUG=true

# .env.production
NODE_ENV=production
PORT=80
DEBUG=false
```

## Integration Examples

### Docker

```bash
# Use with Docker
injectenv --profile docker -e CONTAINER_ID=$(docker ps -q) -- docker exec $CONTAINER_ID python script.py
```

### CI/CD

```bash
# Load CI-specific config
injectenv --profile ci -e BUILD_NUMBER=$CI_BUILD_NUMBER -- npm run deploy
```

### Development Workflow

```bash
# Different configs for different developers
injectenv --profile dev --profile $(whoami) -- python manage.py runserver
```

## Requirements

- Python 3.9+
- python-dotenv

## License

MIT License - see LICENSE file for details.
