import re
import os.path
import codecs
import zipfile
import requests
from threading import Thread
from collections import deque

class Novel:
    _p = re.compile('<p>(.*?)</p>')
    max_thrs = 5

    def __init__(self, url, pagen):
        if not url.endswith('/'):
            url += '/'
        self.url = url
        self.pagen = pagen
        self._ses = None

    @property
    def ses(self):
        if not self._ses:
            self._ses = requests.session()
        return self._ses

    def getall(self):
        print("Getting all...", end='  ', flush = True)
        pages = deque(range(1, self.pagen + 1))
        self.plain = tuple(map(lambda x : "%d.txt" % x, pages))
        def ithr(p):
            while p:
                n = p.pop()
                self.getpage(n)
                print("get", n, end=' ', flush=True)
            print("Get Finish!")
        thrs = [Thread(None, ithr, "NovelGet%d" % i, [pages]) for i in range(self.max_thrs)]
        for t in thrs:
            t.start()
        for t in thrs:
            t.join()

    def check(self):
        if not hasattr(self, 'plain'):
            self.getall()
        if len(self.plain) != self.pagen:
            self.plain = tuple("%d.txt" % i for i in range(1, self.pagen + 1))
        for pn, fn in enumerate(self.plain):
            if not os.path.exists(fn):
                print("Missing page %d" % pn)
                self.getpage(pn)

    def concat(self, concat = 4, prefix="C"):
        self.check()
        cct = self.cct = deque()
        for i in range(1, self.pagen + 1, concat):
            fn = prefix + str((i + 3) // 4) + '.txt'
            cct.append(fn)
            with open(fn, 'x') as wf:
                for a in range(i, i + concat):
                    fn = str(a) + '.txt'
                    try:
                        with codecs.open(fn) as rf:
                            wf.write(rf.read())
                    except:
                        break
    
    def zipall(self):
        if not hasattr(self, 'cct'):
            if not hasattr(self, 'plain'):
                self.getall()
                return self.zipall()
            with zipfile.ZipFile('all.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as f:
                for pf in self.plain:
                    f.write(pf)
            return "Zip All PlainText".split()
        else:
            with zipfile.ZipFile('all.zip', 'w', zipfile.ZIP_DEFALTED, compresslevel=9) as f:
                for cf in self.cct:
                    f.write(cf)
            return "Zip All Concat".split()


    def getpage(self, page):
        fn = str(page) + '.txt'
        if os.path.exists(fn): return
        url = self.url + str(page) + '.html'
        f = self.ses.get(url).text.replace('\u3000', '  ')
        r = self._p.findall(f)
        try:
            with codecs.open(fn, 'x') as f:
                f.write('\n'.join(r))
        except:
            pass
