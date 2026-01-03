FROM jenkins/jenkins:lts
USER root

# Install essential tools, Python, and Git
RUN apt-get update -o Acquire::Retries=3 && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    python3 \
    python3-venv \
    python3-pip \
    libpq-dev \
    python3-dev \
    gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Docker CLI via binary
RUN curl -fsSL https://download.docker.com/linux/static/stable/x86_64/docker-26.1.4.tgz | \
    tar zxvf - --strip-components=1 -C /usr/local/bin/ docker/docker

# Fix permissions for the jenkins user to use Docker
# We create a docker group that matches the host's socket permissions if possible,
# but for now, we'll just ensure the user exists and has a home.
RUN groupadd -g 999 docker || true && \
    usermod -aG docker jenkins

# Install pytest
RUN pip3 install pytest --break-system-packages --no-cache-dir

# Configure Git to be less strict about security checkouts in workspaces
RUN git config --global --add safe.directory '*'

USER jenkins
