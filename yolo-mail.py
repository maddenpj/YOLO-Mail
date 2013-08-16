#!/usr/bin/python

import argparse
import fileinput
import sys
import tempfile
import subprocess
import os

DEFAULT_USER='patrick'
contacts = { 'faiz': 'Faiz Khan', 'patrick': 'Patrick Madden' }


def check_mail(all):
    if all:
        ssh_flags = "ls -ltr /var/crypt/"+ DEFAULT_USER +" | grep -v total | awk '{print $9}'"
    else:
        ssh_flags = "ls -ltr /var/crypt/"+ DEFAULT_USER +" | grep -v total | grep -v READ |  awk '{print $9}'"
    ssh_out = subprocess.check_output(['ssh', 'ssh.yoloinvest.com', ssh_flags])

    if all:
        ssh_out = ssh_out.replace('.READ', '')
    print ssh_out[:-1]


def read_mail(ymail):
    dest = '/var/crypt/' + DEFAULT_USER
    ssh_cmd = ['scp', 'ssh.yoloinvest.com:'+dest+'/'+ymail, '.']
    ssh_out = subprocess.check_output(ssh_cmd)
    gpg_cmd = ['gpg', '-d', ymail]
    gpg_out = subprocess.check_output(gpg_cmd)
    mark_cmd = ['ssh', 'ssh.yoloinvest.com', 'mv '+dest+'/'+ymail+ ' '+dest+'/'+ymail+'.READ']
    mark_out = subprocess.check_output(mark_cmd)
    print gpg_out


def send_mail(recipient, msg_file):
    sys.argv = ['', msg_file]
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






parser = argparse.ArgumentParser(prog='yolo-mail')
subparsers = parser.add_subparsers(dest='subparser_name',
                                   title='subcommands')

check_parser = subparsers.add_parser('check', help='Check your ymail box')
check_parser.add_argument('-a', '--all', help='Fetch all your mail, not just unread', action='store_true')

read_parser = subparsers.add_parser('read', help='Read a ymail')
read_parser.add_argument('ymail', help='Name of the ymail file you want to read')

send_parser = subparsers.add_parser('send', help='Send a ymail, YOLO!')
send_parser.add_argument('recipient', help='The recipient of your ymail')
send_parser.add_argument('msg_file', help='The text file containing your message (default STDIN)',
                                     default='-',
                                     nargs='?')

args = parser.parse_args()
if args.subparser_name == 'check':
    check_mail(args.all)
elif args.subparser_name == 'read':
    read_mail(args.ymail)
elif args.subparser_name == 'send':
    send_mail(args.recipient, args.msg_file)


