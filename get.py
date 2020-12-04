import re
import io
import sys
import codecs
import requests
import argparse
from threading import Thread
from collections import deque
from contextlib import redirect_stdout as rdstdout

def get(page, q=False):
    url = uri.format(page)
    f = requests.get(url).text.replace('\u3000', '  ')
    if not q:print('get page', page, end='\t', flush=True)
    r = re.findall('<p>(.*?)</p>', f)
    file = fn.format(page)
    with codecs.open(file, 'w') as f:
        f.writelines(map(lambda x: x+'\n', r))

def thr(de, q):
    while de:
        try:
            get(de.popleft(), q)
        except Exception as e:
            _e = e
    else:
        raise _e

def check(q):
    import os
    fs = os.listdir('.')
    for n in range(pagen):
        f = fn.format(n)
        if not f in fs:
            get(f, q)

def concat(n, pre='c'):
    for a in range(1, pagen + 1, n):
        cfs = []
        cfn = '%s%d.txt' % (pre, int(a / n) + 1)
        with codecs.open(cfn, 'w') as f:
            for i in range(n):
                try:
                    cfs.append(codecs.open(fn.format(a + i)))
                except:
                    pass
            for cf in cfs:
                f.write(cf.read())
                f.write('\n')


def main():
    global uri, fn, pagen, nums, concatn
    uri = 'http://www.ijjxsw.com/read/11/32981/{}.html'
    fn = '{}.txt'
    pagen = 2299
    nums = 50
    concatn = 3

    parser = argparse.ArgumentParser()
    parser.add_argument('--pagen', '-p', help='page numbers of the novel', default=pagen)
    parser.add_argument('--thread', '-T', help='the threads to download the pages', type=int, default=nums)
    parser.add_argument('--noconcat', '-noc', help='Without concating files', action='store_true')
    parser.add_argument('--concat', '-c', 
            help='The count to concat the files '
            'format as concatfilenums or concatfilenums;concatfileprefix', default='3;c')
    parser.add_argument('--quiet', '-q', help='without output', action='store_true')
    args = parser.parse_args()

    pagen = args.pagen
    nums = args.thread
    cons = args.concat
    q = args.quiet

    de = deque(range(1, pagen+ 1))
    ts = [Thread(target=thr, args=(de,q)) for _ in range(nums)]
    if not q:
        print('Thread use', nums, ', has', pagen, 'pages')
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    check(q)
    if not args.noconcat:
        if ';' in cons:
            concatn, pre = cons.split(';')
        else:
            concatn = cons
        try:
            concatn = int(concatn)
        except:
            print('please enter a correct format arg')
            sys.exit(1)
        concat(concatn, pre)

if __name__ == '__main__':
    main()
