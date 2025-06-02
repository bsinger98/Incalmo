FROM kalilinux/kali-last-release

RUN apt-get update && apt-get install -y python3 python3-pip
RUN apt-get install -y nmap net-tools golang-go curl wget sshpass procps nikto

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
COPY ./ /incalmo
COPY ./config /config
WORKDIR /incalmo

# Install dependencies
RUN uv sync

ENV SERVER_IP=localhost:8888
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/incalmo

# Run the startup script
CMD ["bash", "./docker/attacker/start.sh"]