#!/usr/bin/python

import argparse
import fileinput
import sys
import tempfile
import subprocess
import os

DEFAULT_USER='patrick'


def check_mail(all):
    if all:
        ssh_flags = "ls -ltr /var/crypt/patrick | grep -v total | awk '{print $9}'"
    else:
        ssh_flags = "ls -ltr /var/crypt/patrick | grep -v total | grep -v READ |  awk '{print $9}'"
    ssh_out = subprocess.check_output(['ssh', 'ssh.yoloinvest.com', ssh_flags])

    if all:
        ssh_out = ssh_out.replace('.READ', '')
    print ssh_out[:-1]


def read_mail(ymail):
    pass

def send_mail(recipient, msg_file):
    pass


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
                                     nargs='?',
                                     type=argparse.FileType('r'))

args = parser.parse_args()
if args.subparser_name == 'check':
    check_mail(args.all)
elif args.subparser_name == 'read':
    read_mail(args.ymail)
elif args.subparser_name == 'send':
    send_mail(args.recipient, args.msg_file)


