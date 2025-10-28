# Replicating pjox/cc-crawl-statistics
FROM python:3.12

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3-rpy2 \
    r-cran-ggplot2 \
    graphviz-dev \
    r-base

# Set working directory
WORKDIR /app

# Copy dependency config files
COPY requirements.txt .
COPY requirements_plot.txt .

# Install Python dependencies
RUN pip3 install -r requirements.txt
RUN pip3 install -r requirements_plot.txt

# Copy the current repository files
COPY . .

# Set PYTHONPATH environment variable
ENV PYTHONPATH=/app

# ggplot2 is already installed via r-cran-ggplot2 system package above

# Default command
CMD ["/bin/bash"]