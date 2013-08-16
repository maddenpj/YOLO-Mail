#!/usr/bin/python


import fileinput
import sys
import tempfile
import subprocess
import os


DEFAULT_USER = 'patrick'
DEFAULT_RECEPIENT = 'faiz'


contacts = { 'faiz': 'Faiz Khan', 'patrick': 'Patrick Madden' }

recipient = sys.argv.pop(1) if len(sys.argv) > 1 else DEFAULT_RECEPIENT
msg = ''.join([x for x in fileinput.input()])
f = tempfile.NamedTemporaryFile(delete=False)
f.write(msg)
f.close()

gpg_cmd = 'gpg --yes --no-tty --always-trust --armor -e -u'.split() + [contacts[DEFAULT_USER], '-r', contacts[recipient], f.name]
gpg_out = subprocess.check_output(gpg_cmd)

ssh_cmd = ['scp', f.name + '.asc', 'ssh.yoloinvest.com:/var/crypt/'+ recipient]
ssh_out = subprocess.check_output(ssh_cmd)

os.remove(f.name)
os.remove(f.name +'.asc')

