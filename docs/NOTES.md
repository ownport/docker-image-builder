# Notes

## docker how can I get the list of dependent child images?

http://stackoverflow.com/questions/36584122/docker-how-can-i-get-the-list-of-dependent-child-images

```python
#!/usr/bin/python3
import re
import sys

def desc(image_ids, links):
    if links:
        (image_id, parent_id), *tail = links
        checkid = lambda i: parent_id.startswith(i)
        if any(map(checkid, image_ids)):
            return desc(image_ids | {image_id}, tail)
    return image_ids


def gen_links(lines):
    parseid = lambda s: s.replace('sha256:', '')
    for line in reversed(list(lines)):
        yield list(map(parseid, line.split()))


if __name__ == '__main__':
    image_ids = {sys.argv[1]}
    links = gen_links(sys.stdin.readlines())
    print('\n'.join(desc(image_ids, links)))
```
If you save this as desc.py you could invoke it as follows:
```sh
docker inspect --format='{{.Id}} {{.Parent}}' $(docker images --filter since=f50f9524513f -q) | python3 desc.py f50f9524513f
```