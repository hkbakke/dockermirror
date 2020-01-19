# dockermirror
Docker mirroring for networks without internet connectivity

# CLI usage

    python3 -m dockermirror --help
    
# Client (example implementation)
[dockermirror-client](https://github.com/hkbakke/dockermirror-client)

# API usage
Create archive:

    curl -v -H 'Content-Type: application/json' -XPOST -d '{"images": ["debian:latest", "python:3"]}' http://dockermirror:5000/api/v1/archive

Check url from location header for status:

    curl -v http://localhost:5000/api/v1/job/69e0eb21-7847-481a-96e6-2af2f773efa7

When the job has finished it is possible to check archive information from the status url location header as long as the file still exists:

    curl -v http://dockermirror:5000/api/v1/archive/_sYP7FfCCETSPeaNkQFXH69DLAPORf7ly2EhpGSQ1Ak.tar

# Archive volume
In non-dev environments the docker-compose files are configured to use a named docker volume called archives handled externally. That means that this volume should be preinitialized before starting the containers.

    # Example bind mounted named volume
    docker volume create --opt type=none --opt o=bind --opt device=/path/to/archives --name archives

# Run dockermirror command in docker container

    docker-compose run --rm dockermirror <dockermirror_args>

# Run API server in docker containers

    docker-compose -f api-docker-compose.yml up -d

# Run tests

    docker-compose -f test-docker-compose.yml run --rm dockermirror-test
