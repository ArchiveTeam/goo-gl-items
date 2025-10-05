import re
import sys

import zstandard

PATH_TO_ITEM_MAP = {
    '': 'i',
    'fb': 'f',
    'alerts': 'a',
    'forms': 'g',
    'images': 'im',
    'maps': 'm',
    'news': 'n',
    'photos': 'p',
    'b': 'b'
}


def main(filepath: str):
    with (zstandard.open if filepath.endswith('.zst') else open)(filepath, 'r') as fin, \
        open(filepath+'_items.txt', 'w') as fout:
        for line in fin:
            line = line.strip()
            line += '/'
            if re.search(r'^(?:[^/]*\.)?goo\.gl/', line):
                line = '//' + line
            if re.search(r'^//', line):
                line = 'https:' + line
            line = line.split('?')[0]
            line = line.split('/')
            if len(line) < 3:
                continue
            line[2] = line[2].lower()
            if line[2].startswith('www.'):
                line[2] = line[2].split('.', 1)[1]
            line[2] = line[2].split(':', 1)[0]
            assert ':' not in line[2], line
            line = '/'.join(line)
            for k, v in {
                'goo.gl.gl/': 'goo.gl/',
                'goo.gl./': 'goo.gl/',
                '//.goo.gl/': '//goo.gl/',
                '.ap.goo.gl/': '.app.goo.gl/',
                '/%20': '',
                r'\n': '',
                r'\r': '',
                r'\t': '',
            }.items():
                line = line.replace(k, v)
            if not re.search('^https?://', line) or line.rstrip('/').count('/') == 2:
                continue
            match = re.match(r'^https?://([^/]+)/+((?:[^/]+/)?)([0-9a-zA-Z]+)', line)
            if not match:
                print(line.strip())
                continue
            domain, path, id_ = match.groups()
            domain = domain.lower()
            if domain != 'goo.gl' and not domain.endswith('.app.goo.gl'):
                print(line.strip())
                continue
            path = path.rstrip('/')
            if path not in PATH_TO_ITEM_MAP:
                continue
            if len(id_) > 6 or path in ('forms', 'photos'):
                item_type = PATH_TO_ITEM_MAP[path]
                if item_type == 'i' and domain.endswith('.app.goo.gl'):
                    item_type = 'app:' + domain.rsplit('.', 3)[0]
                    if not re.match('^app:[0-9a-zA-Z]+$', item_type):
                        continue
                    if '.' in item_type:
                        print(line)
                        continue
                fout.write('{}:{}\n'.format(item_type, id_))

if __name__ == '__main__':
    for filepath in sys.argv[1:]:
        main(filepath)

