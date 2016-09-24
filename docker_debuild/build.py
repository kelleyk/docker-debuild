#!/usr/bin/env python3.4
""".

See user_namespaces(7), from which the outline of configure_user_ns() is cribbed, for more information.
"""
from __future__ import division, absolute_import, unicode_literals, print_function

import os
import os.path
import sys
import argparse
import subprocess
import contextlib
import tempfile

from .util import TemporaryDirectory, realpath
from .apt_proxy_utils import get_apt_proxy
from .apt_config_utils import apt_add_source, apt_key_recv, apt_key_fetch


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

    p.add_argument('--env', '-e', action='append',
                   help='Set an environment variable that will be passed to debuild inside the container.'
                   '  Several variables (e.g. DEB_BUILD_OPTIONS) can control how debuild behaves.')
    p.add_argument('--docker-arg', action='append',
                   help='Specify an argument that will be passed to "docker run".')

    p.add_argument('--tmp-path', metavar='path', action='store',
                   help='Path in which a temporary directory will be created for each build.  If not given, '
                   'the default system location (e.g. /tmp) is used.')

    p.add_argument('--apt-source', action='append',
                   help='A package source, in the format of a line from an apt sources.list file.')
    p.add_argument('--apt-key-id', action='append',  # specify keyserver?
                   help='The ID of a key that should be trusted to sign package repositories; the key will be fetched from keyserver.ubuntu.com.')
    p.add_argument('--apt-key-url', action='append',
                   help='The URL of a key that should be trustted to sign package repositories.')
    
    return p


@contextlib.contextmanager
def noop_contextmanager():
    yield
    

def main(argv=None):
    argv = argv or sys.argv
    args = build_parser().parse_args(argv[1:])

    target_suite = args.target_suite
    image_tag = args.image or 'kelleyk/debuild:ubuntu-{}'.format(target_suite)
    build_vol_path = os.path.dirname(os.getcwd())
    target_pkg = os.path.basename(os.getcwd())
    build_args = list(args.build_args)

    apt_proxy_url = args.apt_proxy
    if apt_proxy_url is None:
        print('I: Checking host configuration for apt proxy...', file=sys.stderr)
        apt_proxy_url = get_apt_proxy()
    
    docker_options = list(args.docker_arg or ())
    if apt_proxy_url:
        docker_options.extend(('-e', 'APT_PROXY_URL={}'.format(apt_proxy_url)))
    for env_kv in (args.env or ()):
        # XXX: TODO: Check env_kv for correct format and to avoid duplicate env var names.
        docker_options.extend(('-e', env_kv))

    tmp_path = realpath(args.tmp_path or tempfile.gettempdir())
    with_apt_conf = args.apt_source or args.apt_key_id or args.apt_key_url
    if with_apt_conf:
        tmpdir = TemporaryDirectory(dir=tmp_path, suffix='.docker-debuild')
        
        os.mkdir(os.path.join(tmpdir.pathname, 'sources.list.d'))
        docker_options.extend(('-v', '{}:/etc/apt/sources.list.d:ro'.format(os.path.join(tmpdir.pathname, 'sources.list.d'))))
        for i, line in enumerate(args.apt_source or ()):
            apt_add_source(tmpdir.pathname, str(i), line)
            
        os.mkdir(os.path.join(tmpdir.pathname, 'trusted.gpg.d'))
        docker_options.extend(('-v', '{}:/etc/apt/trusted.gpg.d:ro'.format(os.path.join(tmpdir.pathname, 'trusted.gpg.d'))))
        i = 0
        for key_id in args.apt_key_id or ():
            apt_key_recv(tmpdir.pathname, str(i), key_id)
            i += 1
        for key_url in args.apt_key_url or ():
            apt_key_fetch(tmpdir.pathname, str(i), key_url)
            i += 1
            
    else:
        tmpdir = noop_contextmanager()
        
    with tmpdir:
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
