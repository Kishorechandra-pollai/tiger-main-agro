# Use an official Python runtime as a parent image
FROM python:3.10

# Set environment variables for MSSQL
ENV MSSQL_PORT=1433
ENV MSSQL_USER=psmadmin
ENV MSSQL_DB="psmsqldb"
ENV MSSQL_HOST="postgres"
ENV MSSQL_HOSTNAME="psmsqldb.database.windows.net"
ENV MSSQL_SCHEMA="dbo"
ENV MSSQL_DRIVER="{ODBC Driver 18 for SQL Server}"

# Accept the EULA for the Microsoft ODBC Driver 18 for SQL Server
ENV ACCEPT_EULA=Y

# Update and install necessary tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    gcc \
    g++ \
    gnupg \
    apt-transport-https \
    ca-certificates \
    lsb-release

# Add Microsoft SQL Server Ubuntu repository for the ODBC Driver 18
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Update the sources list and install the MS SQL Server ODBC Driver 18
RUN apt-get update && \
    apt-get install -y msodbcsql18 mssql-tools unixodbc-dev

# Add MSSQL tools to the PATH
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc && \
    /bin/bash -c "source ~/.bashrc"

# Clean the build, removing cache and unnecessary files
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user for the application
RUN useradd -m -s /bin/bash psm

# Create application directory and set permissions
RUN mkdir -p /usr/src/app && chown psm:psm /usr/src/app

# Switch to the new user
USER psm

# Set working directory
WORKDIR /usr/src/app

# Copy the application to the container
COPY --chown=psm:psm /pep-potato-sourcing-matrix-automation/src .

# Upgrade pip and install Python dependencies
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 8000

# Set the command to run the application
CMD ["python", "main.py"]
