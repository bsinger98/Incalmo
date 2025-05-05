FROM ubuntu:22.04

RUN apt-get update && apt-get install -y python3 python3-pip python-is-python3 python3-venv nmap build-essential

RUN apt-get install -y git golang-go

COPY caldera /home/caldera

WORKDIR /home/caldera

# Donut shellcode does not work on ARM chips
RUN pip3 install $(grep -v "donut-shellcode" requirements.txt) --no-cache-dir

RUN pip3 install $(grep -v "donut-shellcode" /home/caldera/plugins/deception/requirements.txt) --no-cache-dir

EXPOSE 8888
# Default HTTPS port for web interface and agent beacons over HTTPS (requires SSL plugin to be enabled)
EXPOSE 8443
# TCP and UDP contact ports
EXPOSE 7010
EXPOSE 7011/udp
# Websocket contact port
EXPOSE 7012
# Default port to listen for DNS requests for DNS tunneling C2 channel
EXPOSE 8853
# Default port to listen for SSH tunneling requests
EXPOSE 8022
# Default FTP port for FTP C2 channel
EXPOSE 2222

ENV PYTHONUNBUFFERED=1

CMD ["python3", "server.py", "--fresh", "--insecure"]