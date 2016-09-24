# kk-debuilder

## Packaging tool suite

This tool is one of four that I use in my `git-buildpackage`-based workflow for creating, forking, and maintaining
Debian (`.deb`) packages.  These tools were written for personal use and most definitely have rough edges.  Please let
me know if you have trouble!  The four are

- [`kk-debuilder`](https://github.com/kelleyk/kk-debuilder)
- [`docker-debuild`](https://github.com/kelleyk/docker-debuild)
- [my `git-buildpackage` fork](https://github.com/kelleyk/git-buildpackage)
- [`apt-config-tool`](https://github.com/kelleyk/apt-config-tool), and

## Overview

`docker-debuild` consists of a series of Docker images (one for each Ubuntu distribution) and a tool that uses those
images to build Debian packages.  I use it from `kk-debuilder`, not directly.

## Getting started

- You will need...

  - This tool (docker-debuild).

  - My `apt-config-tool`, which streamlines the process of installing Debian packages in a Docker container (or a VM).

  - `docker`.

  - The `gpg` command-line utility (if you use any of the `--apt-key-*` options to add extra package repository signing
    keys).

- Run build.sh; it will create a build image for each Ubuntu distribution you want to target.  This image contains only
  the baseline things required to build any Debian package; see `image/apt-config.yaml` for details about what is
  installed.

   - If you run it without any arguments, images will be built for all supported Ubuntu releases.  If you'd like to
     only build a subset of those images, you can provide their names as arguments (e.g. `./build.sh xenial trusty`).

## Usage examples

  TODO

## Features

- Automatic detection of an `apt` proxy if you are using one (including via autodetection, such as
  e.g. `squid-deb-proxy-client`).  You can use `--no-apt-proxy` to prevent this, or `--apt-proxy <proxy-url>` to
  manually specify which proxy should be used.

## Tips

  TODO

## Troubleshooting

Set the `KK_DEBUG_APT_KEYS` environment variable (with e.g. `--docker-arg='-e=KK_DEBUG_APT_KEYS=y`) to see the output
of `apt-key list` inside the container.  This can be helpful if you are having trouble with the `--apt-key-*` options.

