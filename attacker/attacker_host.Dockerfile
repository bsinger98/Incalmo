FROM kalilinux/kali-last-release

RUN apt-get update && apt-get install -y python3 python3-pip

RUN apt-get install -y nmap net-tools golang-go curl wget sshpass

# Create ssh directory
RUN mkdir -p /root/.ssh

# Create ssh key
RUN ssh-keygen -b 2048 -t rsa -f '/root/.ssh/id_rsa' -q -N ""

# Set permissions
RUN chmod 600 /root/.ssh/id_rsa
RUN chmod 700 /root/.ssh

COPY agents/sandcat.bin /tmp/sandcat.bin

RUN chmod +x /tmp/sandcat.bin

CMD ["sh", "-c", "./tmp/sandcat.bin -server http://$SERVER_IP -group red"]

# Install metasploit
RUN apt install -y metasploit-framework
RUN msfconsole
