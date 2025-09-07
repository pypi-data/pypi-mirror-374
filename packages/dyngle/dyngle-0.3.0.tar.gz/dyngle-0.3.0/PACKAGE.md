# Dyngle

## Run lightweight local workflows

Dyngle is a simple workflow runner that executes sequences of commands defined in configuration files. It's like a lightweight combination of Make and a task runner, designed for automating common development and operational tasks.

## Basic usage

Create a configuration file (e.g., `.dyngle.yml`) with your workflows:

```yaml
dyngle:
  operations:
    build:
      - python -m pip install -e .
      - python -m pytest
    deploy:
      - docker build -t myapp .
      - docker push myapp
    clean:
      - rm -rf __pycache__
      - rm -rf .pytest_cache
```

Run an operation:

```bash
dyngle run build
```

## Configuration

Dyngle reads configuration from YAML files. You can specify the config file location using:

- `--config` command line option
- `DYNGLE_CONFIG` environment variable  
- `.dyngle.yml` in current directory
- `~/.dyngle.yml` in home directory

## Workflow structure

Each operation is defined as a list of tasks under `dyngle.operations`. Tasks are executed sequentially using Python's subprocess module for security.

Example with multiple operations:

```yaml
dyngle:
  operations:
    test:
      - python -m unittest discover
      - python -m coverage report
    docs:
      - sphinx-build docs docs/_build
      - open docs/_build/index.html
    setup:
      - python -m venv venv
      - source venv/bin/activate
      - pip install -r requirements.txt
```

## Security

Commands are executed using Python's `subprocess.run()` with arguments split in a shell-like fashion. The shell is not used, which reduces the likelihood of shell injection attacks. However, note that Dyngle is not robust to malicious configuration. 

## Quick installation (MacOS)

```bash
brew install python@3.11
python3.11 -m pip install pipx
pipx install dyngle
```
