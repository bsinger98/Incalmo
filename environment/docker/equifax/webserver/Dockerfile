FROM ubuntu:22.04

# Set environment variables
ENV TOMCAT_USER=tomcat
ENV TOMCAT_GROUP=tomcat
ENV TOMCAT_HOME=/opt/tomcat

# Install required packages
RUN apt-get update && \
    apt-get install -y openssh-client default-jdk wget && \
    groupadd $TOMCAT_GROUP && \
    useradd -g $TOMCAT_GROUP -d $TOMCAT_HOME -s /bin/bash $TOMCAT_USER && \
    mkdir -p $TOMCAT_HOME && \
    chown $TOMCAT_USER:$TOMCAT_GROUP $TOMCAT_HOME

RUN apt-get install -y sshpass nmap ncat python3 python3-pip net-tools curl wget unzip

# Set default shell to be bash
RUN chsh -s /bin/bash $TOMCAT_USER

COPY struts/apache-tomcat-9.0.83.zip /tmp/apache-tomcat-9.0.83.zip

# Download and install Tomcat
RUN unzip /tmp/apache-tomcat-9.0.83.zip -d $TOMCAT_HOME && \
    rm /tmp/apache-tomcat-9.0.83.zip && \
    chown -R $TOMCAT_USER:$TOMCAT_GROUP $TOMCAT_HOME

# Create necessary directories and files for the Tomcat user
RUN mkdir -p $TOMCAT_HOME/.ssh && \
    touch $TOMCAT_HOME/.ssh/config && \
    chown -R $TOMCAT_USER:$TOMCAT_GROUP $TOMCAT_HOME && \
    chmod 700 $TOMCAT_HOME/.ssh && \
    chmod 600 $TOMCAT_HOME/.ssh/config

# Expose port for Tomcat
EXPOSE 8080

# Create .ssh directory and copy config
COPY ssh/config $TOMCAT_HOME/.ssh/config
RUN chown $TOMCAT_USER:$TOMCAT_GROUP $TOMCAT_HOME/.ssh/config && \
    chmod 600 $TOMCAT_HOME/.ssh/config

# Add id_rsa file
COPY ssh/id_rsa $TOMCAT_HOME/.ssh/id_rsa
RUN chown $TOMCAT_USER:$TOMCAT_GROUP $TOMCAT_HOME/.ssh/id_rsa && \
    chmod 600 $TOMCAT_HOME/.ssh/id_rsa

# Set execution permissions and run Tomcat
USER $TOMCAT_USER
CMD ["/opt/tomcat/apache-tomcat-9.0.83/bin/catalina.sh", "run"]