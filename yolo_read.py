#!/usr/bin/python

import subprocess
import sys

msg = sys.argv.pop(1)

ssh_cmd = ['scp', 'ssh.yoloinvest.com:/var/crypt/patrick/'+msg, '.']
ssh_out = subprocess.check_output(ssh_cmd)

gpg_cmd = ['gpg', '-d', msg]
gpg_out = subprocess.check_output(gpg_cmd)

print gpg_out

mark_cmd = ['ssh', 'ssh.yoloinvest.com', 'mv /var/crypt/patrick/'+msg+ ' /var/crypt/patrick/'+msg+'.READ']
mark_out = subprocess.check_output(mark_cmd)
