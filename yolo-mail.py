#!/usr/bin/python

import argparse
import datetime
import fileinput
import json
import os
import subprocess
import sys
import tempfile


DEFAULT_USER='patrick'
contacts = { 'faiz': 'Faiz Khan', 'patrick': 'Patrick Madden' }






#####################
# Mailing Functions #
#####################

def get_max_width(table, index):
    return max([len(row[index]) for row in table])

def pprint_table(table):
    col_paddings = []

    for i in range(len(table[0])):
        col_paddings.append(get_max_width(table, i))

    for row in table:
        print row[0].ljust(col_paddings[0] + 1),
        for i in range(1, len(row)):
            col = row[i].rjust(col_paddings[i] + 2)
            print col,
        print

def convert(input):
    if isinstance(input, dict):
        return {convert(key): convert(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [convert(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

def check_mail(all):
    ssh_flags = "grep metadata /var/crypt/"+ DEFAULT_USER +"/*"
    try:
        ssh_out = subprocess.check_output(['ssh', 'ssh.yoloinvest.com', ssh_flags], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        print 'No messages'
        return

    mails = [convert(json.loads(x.split(':', 1)[1])) for x in ssh_out.split('\n')[:-1]]

    table = [["Name", "Subject", "Sent at:"]]

    if all:
        table[0] += ["Read at:"]

    for i in mails:
        mail = i['metadata']
        line = [[ mail['name'].split('/')[-1], mail['subject'], mail['sent']]]
        if all:
            line[0].append("Unread" if mail['read'] == None else mail['read'])
        elif mail['read'] != None:
           continue
        table += line

    if(len(table) == 1):
        print 'No unread messages'
        return

    pprint_table(table)

def read_mail(ymail):
    dest = '/var/crypt/' + DEFAULT_USER
    f = tempfile.NamedTemporaryFile(delete=False)
    tmp = f.name
    print 'Fetching..'
    ssh_cmd = ['scp', 'ssh.yoloinvest.com:'+dest+'/'+ymail, tmp]
    ssh_out = subprocess.check_output(ssh_cmd)
    gpg_cmd = ['gpg', '-d', tmp]
    gpg_out = subprocess.check_output(gpg_cmd)

    contents = open(tmp).readlines()
    dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None
    metadata = convert(json.loads(contents.pop(0)))
    metadata['metadata']['read'] = datetime.datetime.now()
    contents.insert(0, json.dumps(metadata, default=dthandler) + '\n')

    f = open(tmp, 'w')
    f.write(''.join(contents))
    f.close()

    mark_cmd = ['scp', tmp, 'ssh.yoloinvest.com:'+dest+'/'+ymail]
    mark_out = subprocess.check_output(mark_cmd)
    os.remove(tmp)

    print '\n===== Message =====\n'
    print 'Subject:', metadata['metadata']['subject']
    print gpg_out


def send_mail(recipient, msg_file):
    sys.argv = ['', msg_file]
    msg = ''.join([x for x in fileinput.input()])
    f = tempfile.NamedTemporaryFile(delete=False)
    f.write(msg)
    f.close()

    gpg_cmd = 'gpg --yes --no-tty --always-trust --armor -e -u'.split() + [contacts[DEFAULT_USER], '-r', contacts[recipient], f.name]
    gpg_out = subprocess.check_output(gpg_cmd)

    asc = open(f.name+'.asc').readlines()
    os.remove(f.name)
    os.remove(f.name +'.asc')

    subject = raw_input('Enter a Subject line: ')
    subject = subject if subject != '' else '(No Subject)'

    f = tempfile.NamedTemporaryFile(delete=False)
    metadata = { 'metadata': {
        'name': f.name,
        'subject': subject,
        'sent': datetime.datetime.now(),
        'read': None
        }}
    dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None
    metadata_json = json.dumps(metadata, default=dthandler)

    final_msg = metadata_json + '\n' + ''.join(asc)
    f.write(final_msg)
    f.close()

    ssh_cmd = ['scp', f.name, 'ssh.yoloinvest.com:/var/crypt/'+ recipient]
    sys.stdout.write('Sending...  ')
    ssh_out = subprocess.check_output(ssh_cmd)
    sys.stdout.write('Done.\n')

    os.remove(f.name)




#################
# Parse options #
#################


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


