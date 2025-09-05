# Codeset Gym

A Python package for testing code patches in Docker containers.

## Installation

```bash
pip install -e .
```

## Usage

```bash
docker login -u <USER> -p <PASSWORD> <REPOSITORY>
python -m codeset_gym <instance_id> [repository]
```

## Dependencies

- docker
- junitparser
- datasets

## License

MIT