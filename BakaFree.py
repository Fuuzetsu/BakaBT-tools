#Uses your cookies to search BakaBT for torrents that are freeleech
#Possible features: Small torrents only

import sys
import re
import shutil
import socket
import mechanize
from HTMLParser import HTMLParser

URL_BASE = 'http://bakabt.me'
LIMIT = 2

class Maybe(object):

    def __init__(self, val, nothing=False):
        self.val = val
        self.nothing = nothing

    def __repr__(self):
        if self.is_nothing():
            return 'Nothing'
        return 'Just %s' % self.val

    def is_nothing(self):
        return self.nothing

    def get_value(self):
        if self.nothing:
            raise Maybe.NothingError
        return self.val

    class NothingError(Exception):
        pass


Nothing = Maybe(None, nothing=True)

def Just(v):
    return Maybe(v)



def getLinks(pageSource):
    sections = []
    while '<td class="category"' in pageSource:
        cutOff = pageSource.find('<td class="category"')
        sections.append(pageSource[:cutOff])
        pageSource = pageSource[cutOff + 24:]

    sections.append(pageSource)

    splitAlts = []
    for s in sections:
        if 'Alternative versions:' in s:
            x = s.find('Alternative versions:')
            splitAlts.append(s[:x])
            splitAlts.append(s[x:])
        else:
            splitAlts.append(s)
    fr = 'title="Freeleech">[F]</span>'
    sections = [s for s in sections if fr in s]

    #sections = ripped out sections with freeleech
    extracted = []
    for s in sections:
        extracted.append(re.search(r'<a href="(/\d+[-_\w.]+)" style="color:', s).groups()[0])

    return [ URL_BASE + x for x in extracted ]

def getTorrents(url):
    while True:
        try:
            source = opener.open(URL_BASE + url)
        except:
            sys.stdout.write(URL_BASE + url, 'threw an exception')
        break
    source = source.read().decode("utf8", 'ignore')
    tr = URL_BASE + re.search('<a href="(/download/\d+/\d+/\w+/\d+/[\w_.-]+.torrent)"', source).groups()[0]
    return tr

def download(url):
    if not WINDOZE:
        shutil.os.system('wget -t 10 -T 5 -N -q %s' % url)
    else:
        fileName = shutil.os.path.split(url)[1]
        passed = False
        while not passed:
            while True:
                try:
                    torrentFile = urllib.request.urlopen(url)
                    fileSize = int(torrentFile.headers['Content-Length'])
                    torrentFile = torrentFile.read()
                except:
                    continue
                break
            finalSave = open(fileName, 'wb')
            finalSave.write(torrentFile)
            finalSave.close()

            if shutil.os.path.getsize(fileName) == fileSize:
                passed = True

class BakaParser(HTMLParser):

    waiting_for_pages = False
    page_links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            for a in attrs:
                if a[0] == 'class' and a[1] == 'pager':
                    BakaParser.waiting_for_pages = True

        if BakaParser.waiting_for_pages and tag == 'a':
            for a in attrs:
                if a[0] == 'href':
                    BakaParser.page_links.append(a[1])

    def handle_endtag(self, tag):
        if tag == 'div' and BakaParser.waiting_for_pages:
            BakaParser.waiting_for_pages = False

def search(word):
    request = mechanize.Request('%s/browse.php?q=%s' % (URL_BASE, word))
    response = mechanize.urlopen(request)
    return response.read()

def idt(x):
    return x

def main():
    if len(sys.argv) != 3:
        sys.stdout.write("usage: python BakaFree.py USERNAME PASSWORD")
        sys.exit(2)

    logged_in = login(sys.argv[1], sys.argv[2])

    if logged_in.is_nothing():
        sys.stdout.write('Failed to reach the login page.\n')
    elif logged_in.get_value():
        sys.stdout.write('Successfully logged in as %s\n' % sys.argv[1])
    else:
        sys.stdout.write('Failed to log in.\n')
        sys.exit(3)

    m_links = mapMaybe(mKlesliComp(getLinks, get_page_source), get_pages())

    if m_links.is_nothing():
        sys.stderr.write('Got Nothing in the end.\n')
        sys.exit(3)

    all_links = [ y for x in m_links.get_value() for y in x ]

    sys.stdout.write(all_links.__str__() + '\n')
    sys.stdout.write(len(all_links).__str__() + '\n')

def maybeBind(m, f):
    if m.is_nothing():
        return Nothing

    return f(m.get_value())

def mKlesliComp(f, g):
    return lambda x: maybeBind(g(x), f)


# (a -> b) -> Maybe [a] -> Maybe [b]
def mapMaybe(f, m):
    if m.is_nothing():
        return Nothing
    return Just([ f(x) for x in m.get_value() ])

def get_page_source(url):
    try:
        return Just(mechanize.urlopen(url).read())
    except mechanize.HTTPError:
        sys.stderr.write('HTTPError when fetching %s\n' % url)
        return Nothing


def get_pages():
    try:
        page_url = ('%s/browse.php?ordertype=size&order=1&limit=100' % URL_BASE)
        request = mechanize.Request(page_url)
        response = mechanize.urlopen(request)
        body = response.read()
        response.close()

        parser = BakaParser()
        parser.feed(body)
        pages = int(BakaParser.page_links[-2].split('=')[-1]) + 1
        pages = LIMIT if LIMIT < pages else pages
        return Just([ '%s&page=%d' % (page_url, p) for p in xrange(pages) ])
    except mechanize.HTTPError:
        return Nothing


def login(username, password):
    request = mechanize.Request('%s/login.php' % URL_BASE)
    response = mechanize.urlopen(request)
    forms = mechanize.ParseResponse(response)
    response.close()
    if len(forms) < 3:
        sys.stderr.write('Failed to reach the login page.\n')
        sys.exit(1)

    form = forms[2]
    form['username'] = username
    form['password'] = password
    login_request = form.click()
    try:
        login_response = mechanize.urlopen(login_request)
    except mechanize.HTTPError, login_response:
        sys.stderr.write('HTTPError when logging in...\n')
        return Nothing

    return Just(login_response.geturl() == ('%s/index.php' % URL_BASE))

if __name__ == '__main__':
    main()



# source = opener.open('http://bakabt.com/browse.php?ordertype=size&order=1&limit=100')
# source = source.read().decode("utf8", 'ignore')

# links = getLinks(source)
# pages = getPages(source)
# totalToGet = len(pages)
# for index, page in enumerate(pages):
#     sys.stdout.write('Still need to get %d pages             ' % (totalToGet - index), end = '\r')
#     source = opener.open(URL_BASE + page)
#     source = source.read().decode("utf8", 'ignore')
#     for link in getLinks(source):
#         links.append(link)

# x = open('ExtractsFree.txt', 'w')
# for l in links:
#     x.write(URL_BASE + l + '\n')
# x.close()
# sys.stdout.write('Extracted %d links that are freeleech.\nNow getting links to .torrent files' % len(links))

# totalToGet = len(links)
# torrentFiles = []
# for index, link in enumerate(links):
#     sys.stdout.write('Getting link %d out of %d.        ' % (index + 1, totalToGet), end = '\r')
#     torrentFiles.append(getTorrents(link))

# sys.stdout.write('Got links. Now downloading the files.')
# totalToGet = len(torrentFiles)
# if not shutil.os.path.exists('BakaBT freeleech'):
#     shutil.os.mkdir('BakaBT freeleech')
# shutil.os.chdir('BakaBT freeleech')
# for index, torrent in enumerate(torrentFiles):
#     sys.stdout.write('Downloading .torrent %d out of %d.        ' % (index + 1, totalToGet), end = '\r')
#     download(torrent)


# sys.stdout.write('\nDone.')
