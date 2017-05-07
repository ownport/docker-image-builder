# docker-image-builder

Docker Image Builder, creation of Docker images without Dockerfiles

## How to use

```sh
$ ./target/docker-image-builder
usage: docker-image-builer <command> [<args>]

The list of commands:
   run              run Docker image           
   build            build Docker image
   halt             stop and remove container(-s)

positional arguments:
  command               Subcommand to run

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
```

### Example

The build script
```python
from __future__ import (absolute_import, division, print_function)

def run(ctxt):
    for ret in ctxt.cmd(*[ 'apk update', 'apk add python']):
        print(ret)
```

Run docker-image-builder
```sh
$ ./target/docker-image-builder  build -s alpine:3.5 -c b1 -t ownport/python:alpine-3.5 --build-script examples/simple-build.py --re-run --remove-staging
2017-05-07 22:01:06,486 (builder.docker) [INFO] {"msg": "Starting base container", "image.name": "alpine:3.5", "container.name": "b1", "rerun": true}
2017-05-07 22:01:07,217 (builder.docker) [INFO] {"msg": "Base container was created", "container.id": "d92839628c19ec52402cfa9f8cdd360f132dfaad1a2a4b71e514bcbeb3bdff33"}
2017-05-07 22:01:07,235 (builder.docker) [INFO] {"msg": "Execute command(-s) in the container", "commands.args": [["apk", "update"]], "container.name": "b1"}
2017-05-07 22:01:08,699 (builder.docker) [INFO] {"msg": "Execute command(-s) in the container", "commands.args": [["apk", "add", "python"]], "container.name": "b1"}
fetch http://dl-cdn.alpinelinux.org/alpine/v3.5/main/x86_64/APKINDEX.tar.gz
fetch http://dl-cdn.alpinelinux.org/alpine/v3.5/community/x86_64/APKINDEX.tar.gz
v3.5.2-71-g1050b6acec [http://dl-cdn.alpinelinux.org/alpine/v3.5/main]
v3.5.2-70-gec9876f375 [http://dl-cdn.alpinelinux.org/alpine/v3.5/community]
OK: 7964 distinct packages available
(1/10) Installing libbz2 (1.0.6-r5)
(2/10) Installing expat (2.2.0-r0)
(3/10) Installing libffi (3.2.1-r2)
(4/10) Installing gdbm (1.12-r0)
(5/10) Installing ncurses-terminfo-base (6.0-r7)
(6/10) Installing ncurses-terminfo (6.0-r7)
(7/10) Installing ncurses-libs (6.0-r7)
(8/10) Installing readline (6.3.008-r4)
(9/10) Installing sqlite-libs (3.15.2-r0)
(10/10) Installing python2 (2.7.13-r0)
Executing busybox-1.25.1-r0.trigger
OK: 51 MiB in 21 packages
2017-05-07 22:01:14,971 (builder.docker) [INFO] {"msg": "Committing container into image", "image.name": "ownport/python:alpine-3.5", "container.name": "b1"}
2017-05-07 22:01:16,245 (builder.docker) [INFO] {"msg": "Container committed to the image", "image.name": "ownport/python:alpine-3.5", "image.id": "sha256:9d62674cd442eaa62395c9d2e6786fb37658b8f10a02144ee1065a9cc523ee3f", "container.name": "b1"}
2017-05-07 22:01:16,261 (builder.docker) [INFO] {"msg": "Stopping containers", "container.ids": [["d92839628c19"]]}
2017-05-07 22:01:26,710 (builder.docker) [INFO] {"msg": "Removing containers", "container.ids": [["d92839628c19"]]}

```

## For developers

```sh
$ make compile && ./target/docker-image-builder --help
[INFO] Cleaning directory: /home/dev/github/docker-image-builder/target
[INFO] Cleaning files: *.pyc
[INFO] Cleaning files: .coverage
[INFO] Compiling to binary, docker-image-builder
usage: docker-image-builer <command> [<args>]

The list of commands:
   run              run Docker image           
   build            build Docker image
   halt             stop and remove container(-s)
...
```
