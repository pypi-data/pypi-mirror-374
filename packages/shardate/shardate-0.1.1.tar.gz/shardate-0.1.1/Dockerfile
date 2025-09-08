FROM python:latest

# Set working directory
WORKDIR /app

# Install java
RUN apt update && \
    apt install -y default-jdk && \
    apt clean && \
    rm -rf /var/lib/apt/lists/* && \
    JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:/bin/java::") && \
    echo "JAVA_HOME=${JAVA_HOME}" >> /etc/environment && \
    echo "PATH=${JAVA_HOME}/bin:${PATH}" >> /etc/environment

ENV JAVA_HOME=/usr/lib/jvm/default-java
RUN ln -sf $(readlink -f /usr/bin/java | sed "s:/bin/java::") /usr/lib/jvm/default-java

# Install python application
COPY . .
RUN pip install --upgrade pip && \
    pip install uv && \
    uv venv && \
    uv pip install -e .

CMD ["bash"]