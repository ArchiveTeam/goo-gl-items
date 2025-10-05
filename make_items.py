import os
import string
import typing

import zstandard

CHARS = string.digits + string.ascii_letters
LIST_SIZE = 100000000


def get_ids(length: int, start: str) -> typing.Iterator[str]:
    length -= 1
    for c in CHARS:
        if length == 0:
            yield start + c + '*'
        else:
            yield from get_ids(length, start+c)


def finish_file(f, z, last_id: str):
    z.flush()
    f.flush()
    z.close()
    f.close()
    os.rename(f.name, f.name.rsplit('.', 2)[0]+'-'+last_id.split(':', 1)[1]+'.txt.zst')


def write_files(item_type: str, length: int):
    for i, s in enumerate(get_ids(length, item_type+':')):
        if i % LIST_SIZE == 0:
            f = open(item_type+'_'+s.split(':', 1)[1]+'.txt.zst', mode='wb')
            z = zstandard.open(f, closefd=True, mode='wb')
        z.write(bytes(s+'\n', 'utf8'))
        if (i+1) % LIST_SIZE == 0:
            finish_file(f, z, s)
    finish_file(f, z, s)


def main():
    for item_type, length in {
        'f': 6,
        'a': 6,
        'i': 6,
        'j': 6,
        'm': 5,
        'n': 5
    }.items():
        for l in range(1, length):
            write_files(item_type, l)

# f,fb: 5, 6 (low priority)
#x a,alerts: 5, 6
#x i: 6
# f,forms: too long (low priority)
#x j,images: 6, extra page
#x m,maps: 5, too long
#x n,news: 5
# p,photos: too long (low priority)

if __name__ == '__main__':
    main()

