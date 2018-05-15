#!/usr/bin/env python2.7
# -*- mode: python; encoding: utf-8; -*-

import sys
import os
import os.path
import subprocess

import requests


def apt_add_source(conf_path, sourcelist, line):
    with open(os.path.join(conf_path, 'sources.list.d', '{}.list'.format(sourcelist)), 'w') as f:
        f.write(line)
        f.write('\n')


def apt_key_recv(conf_path, keyring, key_id, keyserver='keyserver.ubuntu.com'):
    keyring_path = os.path.join(conf_path, 'trusted.gpg.d', '{}.gpg'.format(keyring))

    # N.B.: Be careful; apt (at least in Xenial) does not seem to like gpg2 keyrings.
    cmd = ('gpg', '--no-default-keyring', '--keyring', keyring_path, '--keyserver', keyserver, '--recv-keys', key_id)

    try:
        p = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)
    except OSError as exc:
        if exc.errno == 2:
            raise OSError(2, 'No such executable: {}'.format(cmd[0]))
        raise
    p.communicate(sys.stdin)

    os.chmod(keyring_path, 0o644)

    
def apt_key_fetch(conf_path, keyring, url):
    keyring_path = os.path.join(conf_path, 'trusted.gpg.d', '{}.gpg'.format(keyring))
    
    r = requests.get(url)
    with open(keyring_path, 'wb') as f:
        f.write(r.content)
    # XXX: Do we need to pipe things through gpg?
    #    wget -q -O - $URL | sudo gpg --no-default-keyring --keyring /etc/apt/trusted.gpg.d/$KEYRING.gpg --import

    os.chmod(keyring_path, 0o644)
    
