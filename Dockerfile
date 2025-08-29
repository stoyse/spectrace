FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    openjdk-17-jdk \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Download and install Ghidra
WORKDIR /opt
RUN wget -q https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_11.0.3_build/ghidra_11.0.3_PUBLIC_20240410.zip \
    && unzip ghidra_11.0.3_PUBLIC_20240410.zip \
    && rm ghidra_11.0.3_PUBLIC_20240410.zip \
    && mv ghidra_11.0.3_PUBLIC /opt/ghidra

# Add Ghidra to PATH
ENV GHIDRA_INSTALL_DIR=/opt/ghidra
ENV PATH="${GHIDRA_INSTALL_DIR}/support:${PATH}"

# Create app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api/ .

# Create directories for temporary files
RUN mkdir -p /tmp/ghidra_projects /tmp/uploads

# Set permissions
RUN chmod +x /opt/ghidra/support/analyzeHeadless

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]