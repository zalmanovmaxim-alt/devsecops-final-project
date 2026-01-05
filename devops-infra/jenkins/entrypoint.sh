#!/bin/bash
set -e

# Get the group ID of the docker socket mounted from host
DOCKER_SOCKET_GID=$(stat -c '%g' /var/run/docker.sock)

# Check if the 'docker' group exists
if getent group docker > /dev/null 2>&1; then
    # If it exists, checking if it matches the socket GID
    CURRENT_GID=$(getent group docker | cut -d: -f3)
    if [ "$CURRENT_GID" != "$DOCKER_SOCKET_GID" ]; then
        echo "Updating docker group GID from $CURRENT_GID to $DOCKER_SOCKET_GID"
        groupmod -g ${DOCKER_SOCKET_GID} docker
    fi
else
    # Create the group with the socket's GID
    echo "Creating docker group with GID $DOCKER_SOCKET_GID"
    groupadd -g ${DOCKER_SOCKET_GID} docker
fi

# Ensure jenkins user is part of the docker group
usermod -aG docker jenkins

# Execute the passed command (jenkins) as the jenkins user
echo "Starting Jenkins..."
exec gosu jenkins "$@"
