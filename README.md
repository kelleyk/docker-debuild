=========================
What you need
=========================

- This tool (docker-debvuild).

- My apt-config-tool, which streamlines the process of installing Debian packages in a Docker
  container (or a VM).

=========================
Works well with
=========================

- kk-debuilder, my workflow tool that wraps git-buildpackage and uses this tool.

=========================
Getting started
=========================

- Run build.sh; it will create a build image for each Ubuntu release you want to target.  This image
  contains only the baseline things required to build any Debian package; see image/apt-config.yaml
  for details about what is installed.

=========================
Using an apt proxy
=========================
