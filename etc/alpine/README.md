# etc files for Alpine dists

The directory contains group and passwd files which are required for 
mount host directories with host user rights. The files copied from base
alpine:3.5 image

These files shall be mounted to the container as volumes.
 
Example:
```sh
docker run -ti \
    -v $(pwd)/etc/group:/etc/group:ro -v $(pwd)/etc/passwd:/etc/passwd:ro \
    -u $( id -u $USER ):$( id -g $USER ) \
    some-image:lastest /bin/sh
```

The idea was taken from https://denibertovic.com/posts/handling-permissions-with-docker-volumes/

