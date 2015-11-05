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

  - This tool (docker-debvuild).

  - My `apt-config-tool`, which streamlines the process of installing Debian packages in a Docker container (or a VM).

- Run build.sh; it will create a build image for each Ubuntu distribution you want to target.  This image contains only
  the baseline things required to build any Debian package; see `image/apt-config.yaml` for details about what is
  installed.

## Usage examples

  TODO

## Features

- Automatic detection of an `apt` proxy if you are using one (including via autodetection, such as
  e.g. `squid-deb-proxy-client`).  You can use `--no-apt-proxy` to prevent this, or `--apt-proxy <proxy-url>` to
  manually specify which proxy should be used.

## Tips

  TODO
