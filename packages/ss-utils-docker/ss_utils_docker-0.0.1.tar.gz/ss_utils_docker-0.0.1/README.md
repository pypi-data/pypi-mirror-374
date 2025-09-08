Simple Utilities for Docker.

## Installation

```bash
uv add ss-utils-docker
```

## Usage

```sh
# [in project_dir where .env exists]
ss-docker build
ss-docker push

# alternative: specify the environment file
ss-docker build --pth-env .env.prod
ss-docker push --pth-env .env.prod
```
