#!/usr/bin/env python3.4
""".

See user_namespaces(7), from which the outline of configure_user_ns() is cribbed, for more information.
"""
import os
import os.path
import sys
import time
import signal
import argparse
import contextlib
import subprocess


def build_parser():
    p = argparse.ArgumentParser()
    # p.add_argument('target_pkg', action='store')
    p.add_argument('target_suite', action='store')
    # p.add_argument('build_vol_path', action='store')
    p.add_argument('build_args', nargs='*')
    p.add_argument('--image', metavar='docker-image-ref', action='store', default=None)
    return p


def main(argv=None):
    argv = argv or sys.argv
    args = build_parser().parse_args(argv[1:])

    target_suite = args.target_suite
    image_tag = args.image or 'kelleyk/debuild:ubuntu-{}'.format(target_suite)
    build_vol_path = os.path.dirname(os.getcwd())
    target_pkg = os.path.basename(os.getcwd())
    build_args = list(args.build_args)

    # TODO: Autodetect.
    apt_proxy_url = 'http://192.168.0.1:3142/'
    
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
        if container_id is not None:
            subprocess.check_call(('docker', 'rm', '-f', container_id))


if __name__ == '__main__':
    main()
