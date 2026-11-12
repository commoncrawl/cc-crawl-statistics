# Replicating pjox/cc-crawl-statistics
FROM python:3.12

# Install system dependencies
#  - git, jq, awscli: used by the shell scripts (get_stats.sh, plot.sh)
#  - graphviz-dev: required to build and run pygraphviz (plot/overlap.py)
#  - fontconfig, fonts-liberation (Helvetica alternative), fonts-dejavu: fonts used by matplotlib
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    jq \
    awscli \
    graphviz-dev \
    fontconfig \
    fonts-liberation \
    fonts-dejavu \
    && fc-cache -fv \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# uv installs the Python packages pinned in uv.lock
RUN pip3 install --no-cache-dir uv==0.13.7

# Copy dependency config files (first for cache)
COPY pyproject.toml uv.lock ./

# Install the Python packages into /opt/venv, outside /app, so they stay
# available when the repository is mounted over /app. --locked fails instead
# of updating uv.lock when it doesn't match pyproject.toml.
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH=/opt/venv/bin:$PATH
RUN uv sync --locked --all-groups --no-cache

# Copy the remaining repository files
COPY stats/crawler ./stats/crawler
COPY plots/ ./plots/
COPY plot/ ./plot/
COPY tests/ ./tests/

COPY *.sh ./
COPY *.py ./
COPY _config.yml ./

# Set environment variables
ENV PYTHONPATH=/app

# Plot library: only matplotlib is supported in this image
ENV PLOTLIB=matplotlib

# aws cli: use the system CA bundle instead of its own copy
ENV AWS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Default command
CMD ["./get_stats_and_plot.sh"]
