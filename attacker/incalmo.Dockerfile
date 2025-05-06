FROM kalilinux/kali-last-release

RUN apt-get update && apt-get install -y python3 python3-pip
RUN apt-get install -y nmap net-tools golang-go curl wget sshpass build-essential libssl-dev libffi-dev python3-dev

# Create ssh directory and server directory
RUN mkdir -p /root/.ssh
RUN mkdir -p /server

# Create ssh key
RUN ssh-keygen -b 2048 -t rsa -f '/root/.ssh/id_rsa' -q -N ""

# Set key permissions
RUN chmod 600 /root/.ssh/id_rsa
RUN chmod 700 /root/.ssh

# Copy agets and server files
COPY /attacker/agents/sandcat.bin /tmp/sandcat.bin
COPY /attacker/c2_server/server.py /server/server.py
COPY /attacker/c2_server/Instruction.py /server/Instruction.py
COPY /attacker/c2_server/requirements.txt /server/requirements.txt

# Give permissions to the files
RUN chmod +x /tmp/sandcat.bin
RUN chmod +x /server/server.py
RUN chmod +x /server/Instruction.py

# Install requirements
RUN pip3 install --break-system-packages -r /server/requirements.txt

ENV SERVER_IP=0.0.0.0:8888

# Create startup script
RUN echo '#!/bin/bash\n\
        python3 /server/server.py &\n\
        /tmp/sandcat.bin -server http://$SERVER_IP -group red\n\
        ' > /start.sh && chmod +x /start.sh

# Run the startup script
CMD ["/start.sh"]