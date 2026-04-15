# Base image: ubuntu:22.04
FROM ubuntu:22.04

# ARGs
# https://docs.docker.com/engine/reference/builder/#understand-how-arg-and-from-interact
ARG TARGETPLATFORM=linux/amd64,linux/arm64
ARG DEBIAN_FRONTEND=noninteractive

# neo4j 2025.08.0 installation (match GDS v2.21.0) and some cleanup
RUN apt-get update && \
    apt-get install -y wget gnupg software-properties-common && \
    wget -O - https://debian.neo4j.com/neotechnology.gpg.key | apt-key add - && \
    echo 'deb https://debian.neo4j.com stable latest' > /etc/apt/sources.list.d/neo4j.list && \
    add-apt-repository universe && \
    apt-get update && \
    apt-get install -y nano unzip neo4j=1:2025.08.0 python3-pip && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# ---------------------------------------------------------------------
#  TODO 

# 1. Working directory setup
WORKDIR /cse511
RUN mkdir -p /cse511

# 2. Install Java 21 and system dependencies
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        wget \
        curl \
        openjdk-21-jdk && \
    rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME="/usr/lib/jvm/java-21-openjdk-amd64"
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# 3. Install Python dependencies
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir pandas neo4j pyarrow

# 4. Fetch March 2022 NYC Yellow Taxi data
ADD https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2022-03.parquet \
    /cse511/yellow_tripdata_2022-03.parquet

# 5. Include Python script
COPY ./data_loader.py ./data_loader.py

# 6. Create and configure Neo4j import directory
RUN install -d -m 755 /var/lib/neo4j/import

# 7. Get Neo4j GDS plugin (v2.21.0)
ADD https://github.com/neo4j/graph-data-science/releases/download/2.21.0/neo4j-graph-data-science-2.21.0.jar \
    /var/lib/neo4j/plugins/neo4j-graph-data-science-2.21.0.jar

# 8. Configure Neo4j settings
RUN { \
      echo "dbms.default_listen_address=0.0.0.0"; \
      echo "dbms.security.procedures.unrestricted=gds.*,apoc.*"; \
      echo "dbms.security.procedures.allowlist=gds.*,apoc.*"; \
      echo "dbms.security.auth_enabled=true"; \
    } >> /etc/neo4j/neo4j.conf

# 9. Initialize default Neo4j password
RUN neo4j-admin dbms set-initial-password "graphprocessing"

# ---------------------------------------------------------------------
RUN chmod +x /cse511/data_loader.py && \
    neo4j start && \
    python3 /cse511/data_loader.py && \
    neo4j stop

# Expose neo4j ports
EXPOSE 7474 7687

# Start neo4j service and show the logs on container run
CMD ["/bin/bash", "-c", "neo4j start && tail -f /dev/null"]
