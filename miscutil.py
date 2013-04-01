import re
import sys
import shutil
import urllib
import mechanize
import os.path
from HTMLParser import HTMLParser

URL_BASE = 'http://bakabt.me'

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

class Either(object):

    def __init__(self, val, left=False):
        self.val = val
        self.left = left

    def __repr__(self):
        if self.is_left():
            return 'Left (%s)' % self.val
        return 'Right (%s)' % self.val

    def is_left(self):
        return self.left

    def get_value(self):
        return self.val

    def bind(self, f):
        if self.is_left():
            return self
        return Right(f(self.get_value()))

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
Just = Maybe
Left = lambda x: Either(x, left=True)
Right = Either


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
        extracted.append(re.search(r'<a href="(/\d+[-_' +
                                   r'\w.]+)" style="color:', s).groups()[0])

    return [ URL_BASE + x for x in extracted ]


def get_torrent_url(url):
    source = get_page_source(url)
    f = lambda x: URL_BASE + re.search(
        r'<a href="(/download/\d+/\d+/'
        + r'\w+/\d+/[\w_.-]+.torrent)"', x).groups()[0]
    return maybeBind(source, f)

def download(url):
    filename = shutil.os.path.split(url)[1]
    urllib.urlretrieve (url, os.path.join('downloads', filename))
    with open(filename, 'wb') as f:
        f.write(filename)

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

def get_page_source(url):
    try:
        return Just(mechanize.urlopen(url).read())
    except mechanize.HTTPError:
        sys.stderr.write('HTTPError when fetching %s\n' % url)
        return Nothing


def get_pages(limit=None):
    try:
        page_url = ('%s/browse.php?ordertype=size&order=1&limit=10' % URL_BASE)
        request = mechanize.Request(page_url)
        response = mechanize.urlopen(request)
        body = response.read()
        response.close()

        parser = BakaParser()
        parser.feed(body)
        pages = int(BakaParser.page_links[-2].split('=')[-1]) + 1
        pages = limit if limit != None and limit < pages else pages
        return Just([ '%s&page=%d' % (page_url, p) for p in xrange(pages) ])
    except mechanize.HTTPError:
        return Nothing

def get_bonus_links(page_source):
    sections = []
    while '<td class="category"' in page_source:
        cutOff = page_source.find('<td class="category"')
        sections.append(page_source[:cutOff])
        page_source = page_source[cutOff + 20:]

    splitAlts = []
    for s in sections:
        if 'Alternative versions:' in s:
            x = s.find('Alternative versions:')
            splitAlts.append(s[:x])
            h = s[x:]
            while '<tr class="torrent_alt' in h:
                x = h.find('<tr class="torrent_alt')
                z = h.find('</tr>')
                splitAlts.append(s[x:z + 5])
                h = h[z + 5:]
        else:
            splitAlts.append(s)

    bn = '<img src="/images/pixel.gif" class="icon bonusbig" alt="Bonus" title="Bonus"/>'
    fr = '<span class="success" title="Freeleech">[F]</span>'

    sections = [s for s in splitAlts if bn in s and fr in s]

    #sections = ripped out sections with both, bonus and freeleech
    extracted = []
    for s in sections:
        e = re.search(r'<a href="(/\d+[\w\d-]+.html)" style="color: #[\d\w]+;">', s)
        #e = re.search(r'<a href="(/\d+[-][-_\w\d.]+.html)"', s)
        if not e == None:
            extracted.append(e.groups()[0])

    if extracted == []:
        print('No appropriate torrents to download.')
    return extracted

def get_bonus_pages(page_source):
    page_source = page_source[page_source.find('<div class="pager">') + len('<div class="pager">'):]
    page_source = page_source[:page_source.find('</div>')]
    pages = re.findall(r'<a href="(/browse.php\?ordertype=size&amp;bonus=1&amp;q=&amp;only=1&amp;order=1&amp;limit=\d+&amp;page=\d+)" class="">\d', page_source)
    return pages

def search(word):
    request = mechanize.Request('%s/browse.php?q=%s' % (URL_BASE, word))
    response = mechanize.urlopen(request)
    return response.read()
