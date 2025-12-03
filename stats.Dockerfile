# Replicating pjox/cc-crawl-statistics
FROM python:3.12

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3-rpy2 \
    r-cran-ggplot2 \
    graphviz-dev \
    r-base jq \
    awscli

# Set working directory
WORKDIR /app

# Copy dependency config files (first for cache)
COPY requirements.txt .
COPY requirements_plot.txt .

# Install Python dependencies
RUN pip3 install -r requirements.txt
RUN pip3 install -r requirements_plot.txt

# Copy the remaining repository files
COPY stats/crawler ./stats/crawler
COPY plots/ ./plots/
COPY plot/ ./plot/
COPY tests/ ./tests/

COPY *.sh ./
COPY *.py ./
COPY _config.yml ./

# Set PYTHONPATH environment variable
ENV PYTHONPATH=/app

# ggplot2 is already installed via r-cran-ggplot2 system package above

# Default command
CMD ["./get_stats_and_plot.sh"]