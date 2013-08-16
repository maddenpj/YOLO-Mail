#!/usr/bin/python

import subprocess
import sys


ssh_unread_cmd = ['ssh', 'ssh.yoloinvest.com', "ls -ltr /var/crypt/patrick | grep -v total | grep -v READ |  awk '{print $9}'"]
ssh_all_cmd = ['ssh', 'ssh.yoloinvest.com', "ls -ltr /var/crypt/patrick | grep -v total |  awk '{print $9}'"]

ssh_out = subprocess.check_output(ssh_unread_cmd)
print ssh_out
