FROM ubuntu:latest


RUN apt-get update && \
    apt-get install -y openssh-server \
    curl \
    wget \
    gnupg \
    net-tools \
    iproute2 \
    dnsutils \
    nmap \
    telnet \
    nano \
    python3 \
    python3-pip \
    postgresql-client \
    redis-tools \
    openfortivpn \
    ssh \
    rsync \
    ppp \
    sshpass \
    && apt-get clean



CMD ["/bin/bash","-c", "while true; do sleep 30; done"]