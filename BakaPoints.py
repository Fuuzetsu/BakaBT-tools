#Uses your cookies to search BakaBT for torrents that are freeleech AND bonus
#Possible features: Small torrents with bonus points download, check over time for new torrents
#using wget because it just werks. Change WINDOZE to True if you don't have wget
#>comments

import re
import shutil
import socket
import http.cookiejar
import urllib.request
import urllib.parse
import urllib.error
from miscutil import *

URL_BASE = 'http://bakabt.me'

def getLinks(pageSource):
    sections = []
    while '<td class="category"' in pageSource:
        cutOff = pageSource.find('<td class="category"')
        sections.append(pageSource[:cutOff])
        pageSource = pageSource[cutOff + 20:]

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

def getPages(pageSource):
    pageSource = pageSource[pageSource.find('<div class="pager">') + len('<div class="pager">'):]
    pageSource = pageSource[:pageSource.find('</div>')]
    pages = re.findall(r'<a href="(/browse.php\?ordertype=size&amp;bonus=1&amp;q=&amp;only=1&amp;order=1&amp;limit=\d+&amp;page=\d+)" class="">\d', pageSource)
    return pages



#Main
if not USERNAME or not PASSWORD:
    print('Username or password can\'t be empty.')
    shutil.os._exit(1)
try:
    details = urllib.parse.urlencode({'username': USERNAME, 'password': PASSWORD})
    details = details.encode('ascii')
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.open(URL_BASE + '/login.php', details)
    ResponseData = opener.open(URL_BASE)
    cookies = ResponseData.info()['set-cookie']
    ResponseData = ResponseData.read().decode("utf8", 'ignore')
    ResponseFail = 'False'
except urllib.error.HTTPError as e:
    ResponseData = e.read().decode("utf8", 'ignore')
    ResponseFail = 'False'
except urllib.error.URLError: ResponseFail = 'True'
except socket.error: ResponseFail = 'True'
except socket.timeout: ResponseFail = 'True'
except UnicodeEncodeError: print("[x]  Encoding Error"); ResponseFail = 'True'

if ResponseFail == 'True':
    print('Failed to connect. Try again.')
    shutil.os._exit(1)

if not USERNAME in ResponseData:
    print('Failed to log in.')
    shutil.os._exit(1)
else:
    print('Logged in as %s' % USERNAME)


source = opener.open('http://bakabt.com/browse.php?ordertype=size&bonus=1&q=&only=1&order=1&limit=100&page=0')
source = source.read().decode("utf8", 'ignore')

links = getLinks(source)
pages = getPages(source)
totalToGet = len(pages)
for index, page in enumerate(pages):
    print('Still need to get %d pages             ' % (totalToGet - index), end = '\r')
    source = opener.open(URL_BASE + page)
    source = source.read().decode("utf8", 'ignore')

    for link in getLinks(source):
        links.append(link)

x = open('Extracts.txt', 'w')
for l in links:
    x.write(URL_BASE + l + '\n')
x.close()
print('Extracted %d links that are bonus and freeleech.\nNow getting links to .torrent files' % len(links))

totalToGet = len(links)
torrentFiles = []
for index, link in enumerate(links):
    print('Getting link %d out of %d.        ' % (index + 1, totalToGet), end = '\r')
    torrentFiles.append(getTorrents(link))

print('Got links. Now downloading the files.')
totalToGet = len(torrentFiles)
if not shutil.os.path.exists('BakaBT torrents script'):
    shutil.os.mkdir('BakaBT torrents script')
shutil.os.chdir('BakaBT torrents script')
for index, torrent in enumerate(torrentFiles):
    print('Downloading .torrent %d out of %d.        ' % (index + 1, totalToGet), end = '\r')
    download(torrent)


print('\nDone.')
