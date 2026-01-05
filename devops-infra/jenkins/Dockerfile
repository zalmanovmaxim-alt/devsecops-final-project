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
    python3-psycopg2 \
    python3-dev \
    gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Docker CLI via binary
RUN curl -fsSL https://download.docker.com/linux/static/stable/x86_64/docker-26.1.4.tgz | \
    tar zxvf - --strip-components=1 -C /usr/local/bin/ docker/docker

# JCasC Configuration
ENV CASC_JENKINS_CONFIG /var/jenkins_home/casc_configs/jenkins.yaml
COPY jenkins.yaml /var/jenkins_home/casc_configs/jenkins.yaml

# Install pytest
RUN pip3 install pytest --break-system-packages --no-cache-dir

# Install Jenkins plugins
RUN jenkins-plugin-cli --plugins \
    blueocean \
    docker-workflow \
    workflow-aggregator \
    git \
    configuration-as-code \
    job-dsl

# Install gosu for easy user switching in entrypoint
RUN set -eux; \
    apt-get update; \
    apt-get install -y gosu; \
    rm -rf /var/lib/apt/lists/*; \
    # Verify that the binary works
    gosu nobody true

# Configure Git to be less strict about security checkouts in workspaces
RUN git config --global --add safe.directory '*'

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/usr/bin/tini", "--", "/usr/local/bin/jenkins.sh"]
