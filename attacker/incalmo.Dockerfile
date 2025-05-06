FROM kalilinux/kali-last-release

RUN apt-get update && apt-get install -y python3 python3-pip
RUN apt-get install -y nmap net-tools golang-go curl wget sshpass procps

RUN pip install --break-system-packages uv

COPY uv.lock /server/uv.lock
COPY pyproject.toml /server/pyproject.toml

# Create ssh directory and server directory
RUN mkdir -p /root/.ssh
RUN mkdir -p /server

# Create ssh key
RUN ssh-keygen -b 2048 -t rsa -f '/root/.ssh/id_rsa' -q -N ""

# Set key permissions
RUN chmod 600 /root/.ssh/id_rsa
RUN chmod 700 /root/.ssh

# Copy agents and server files
COPY /attacker/agents/sandcat.bin /tmp/sandcat.bin
COPY /attacker/c2_server /server
COPY /attacker/start.sh /start.sh

# Give permissions to the files
RUN chmod +x /tmp/sandcat.bin
RUN chmod +x /server/server.py
RUN chmod +x /server/Instruction.py
RUN chmod +x /start.sh

ENV SERVER_IP=localhost:8888
ENV PYTHONUNBUFFERED=1
WORKDIR /server

# Run the startup script
CMD ["/start.sh"]