#!/usr/bin/env python3.4
""".

See user_namespaces(7), from which the outline of configure_user_ns() is cribbed, for more information.
"""
from __future__ import division, absolute_import, unicode_literals, print_function

import os
import os.path
import sys
import time
import signal
import argparse
import contextlib
import subprocess

from .apt_proxy_utils import get_apt_proxy


def build_parser():
    p = argparse.ArgumentParser()
    # p.add_argument('target-pkg', action='store', dest='target_pkg')
    # p.add_argument('build-vol-path', action='store', dest='build_vol_path')
    p.add_argument('target_suite', action='store')
    p.add_argument('build_args', nargs='*')
    p.add_argument('--image', metavar='docker-image-ref', action='store', default=None)

    p.add_argument('--apt-proxy', metavar='proxy-url', action='store', default=None, dest='apt_proxy',
                   help='Explicitly specify the URL of an apt proxy that should be used, such as '
                   '"http://10.0.0.1:3142/".  If not given, the default behavior is to use the '
                   'host\'s apt proxy configuration.')
    p.add_argument('--no-apt-proxy', action='store_const', const=False, dest='apt_proxy',
                   help='Prevent the use of any apt proxy.')

    p.add_argument('--no-rm', '--no-remove-container', action='store_false', dest='remove_container',
                   help='Do not automatically remove the container after the build ends.')

    # p.add_argument('--source-only', action='store_true',
    #                help='Build only source packages; do not build binary packages.  (This option is '
    #                'appropriate for preparing packages to be uploaded to Launchpad.)')
    
    return p


def main(argv=None):
    argv = argv or sys.argv
    args = build_parser().parse_args(argv[1:])

    target_suite = args.target_suite
    image_tag = args.image or 'kelleyk/debuild:ubuntu-{}'.format(target_suite)
    build_vol_path = os.path.dirname(os.getcwd())
    target_pkg = os.path.basename(os.getcwd())
    build_args = list(args.build_args)

    # if args.source_only:
    #     # We always build unsigned packages ('-uc -us') because we don't want to deal with getting keys into
    #     # the build containers and the ensuing security mess.  The packages can be signed out here in the
    #     # host environment with the user's keychain.
    #     build_args.extend(('-S', '-us', 'uc'))

    # TODO: Autodetect.
    apt_proxy_url = args.apt_proxy
    if apt_proxy_url is None:
        print('I: Checking host configuration for apt proxy...', file=sys.stderr)
        apt_proxy_url = get_apt_proxy()
    
    docker_options = []
    if apt_proxy_url:
        docker_options.extend(('-e', 'APT_PROXY_URL={}'.format(apt_proxy_url)))

    container_id = None
    try:
        container_id = subprocess.check_output(
            ['docker', 'create',
             '-v', '{}:/build/buildd:rw'.format(build_vol_path)] +
            docker_options +
            [image_tag,
             '/entry.sh', target_pkg, target_suite] +
            build_args).strip()

        p = subprocess.Popen(
            ('docker', 'start', '--attach=true', '--interactive=true', container_id),
            # stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            stdout=sys.stdout, stderr=sys.stderr,
        )

        container_pid = int(subprocess.check_output(
            ('docker', 'inspect', '--format={{.State.Pid}}', container_id)).strip())
        
        p.wait()

        # XXX: This is a horrible hack, but without it, gbp will fail to clean its temporary export and blow up.
        # XXX: The 'real' fix is to unshare the user namespace and map root in the build container to our EUID out here.
        subprocess.check_call(('sudo', 'chown', '-R', '{}:{}'.format(os.geteuid(), os.getegid()), build_vol_path))

    finally:
        if container_id is not None and args.remove_container:
            subprocess.check_call(('docker', 'rm', '-f', container_id))


if __name__ == '__main__':
    main()
