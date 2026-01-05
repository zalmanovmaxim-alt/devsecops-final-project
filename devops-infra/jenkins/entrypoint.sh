#!/bin/bash
set -e

DOCKER_SOCKET_GID=$(stat -c '%g' /var/run/docker.sock)
echo "Docker socket GID is: $DOCKER_SOCKET_GID"

# Check if a group with this GID already exists
if getent group "$DOCKER_SOCKET_GID" > /dev/null 2>&1; then
    TARGET_GROUP=$(getent group "$DOCKER_SOCKET_GID" | cut -d: -f1)
    echo "Group with GID $DOCKER_SOCKET_GID already exists: $TARGET_GROUP"
else
    # GID doesn't exist. Check if 'docker' group name exists
    if getent group docker > /dev/null 2>&1; then
        echo "Group 'docker' exists but has different GID. Updating..."
        groupmod -g "$DOCKER_SOCKET_GID" docker
    else
        echo "Creating group 'docker' with GID $DOCKER_SOCKET_GID"
        groupadd -g "$DOCKER_SOCKET_GID" docker
    fi
    TARGET_GROUP="docker"
fi

echo "Adding jenkins user to group: $TARGET_GROUP"
usermod -aG "$TARGET_GROUP" jenkins

echo "Starting Jenkins..."
exec gosu jenkins "$@"
