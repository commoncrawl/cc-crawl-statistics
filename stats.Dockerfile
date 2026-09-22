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

# Copy dependency config files (first for cache)
COPY requirements.txt .
COPY requirements_plot.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install --no-cache-dir -r requirements_plot.txt

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

# Default command
CMD ["./get_stats_and_plot.sh"]
