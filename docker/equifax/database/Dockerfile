FROM ubuntu:22.04

# Install SSH server
RUN apt-get update && \
    apt-get install -y openssh-server && \
    mkdir /var/run/sshd && \
    echo 'root:root' | chpasswd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

RUN apt-get install -y sshpass nmap ncat python3 python3-pip net-tools curl wget

# Create user database with home directory
ENV DB_USER=database
RUN useradd -m $DB_USER && \
    chown -R $DB_USER:$DB_USER /home/$DB_USER

# Set default shell to be bash
RUN chsh -s /bin/bash $DB_USER

# Copy data
COPY data.json /home/$DB_USER/data.json

# Expose port for SSH
EXPOSE 22

# Create .ssh directory and authorized_keys file
COPY authorized_keys /home/$DB_USER/.ssh/authorized_keys
RUN chown $DB_USER:$DB_USER /home/$DB_USER/.ssh/authorized_keys && \
    chown $DB_USER:$DB_USER /home/$DB_USER/.ssh/ && \
    chmod 600 /home/$DB_USER/.ssh/authorized_keys && \
    chmod 700 /home/$DB_USER/.ssh

# Set execution permissions and run SSH server
CMD ["/usr/sbin/sshd", "-D"]