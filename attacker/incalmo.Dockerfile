FROM kalilinux/kali-last-release

RUN apt-get update && apt-get install -y python3 python3-pip
RUN apt-get install -y nmap net-tools golang-go curl wget sshpass procps

RUN pip install --break-system-packages uv

# Create ssh directory and server directory
RUN mkdir -p /root/.ssh
RUN mkdir -p /server

# Create ssh key
RUN ssh-keygen -b 2048 -t rsa -f '/root/.ssh/id_rsa' -q -N ""

# Set key permissions
RUN chmod 600 /root/.ssh/id_rsa
RUN chmod 700 /root/.ssh

# Copy attacker files
COPY /attacker /attacker
WORKDIR /attacker

# Install dependencies
RUN uv sync

ENV SERVER_IP=localhost:8888
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/attacker

# Run the startup script
CMD ["bash", "./start.sh"]