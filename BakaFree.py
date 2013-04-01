#Uses your cookies to search BakaBT for torrents that are freeleech
#Possible features: Small torrents only
#>comments

import re
import shutil
import socket
import http.cookiejar
import urllib.request
import urllib.parse
import urllib.error

USERNAME = ''
PASSWORD = ''
URL_BASE = 'http://bakabt.com'
PAGES = 4
STARTING = 1

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

    return extracted

def getPages(pageSource):
    pages = []
    for i in range(STARTING, PAGES):
        pages.append('/browse.php?ordertype=size&amp%%3Border=1&amp%%3Blimit=100&amp%%3Bpage=1&order=1&limit=100&page=%d' % i)
    return pages

def getTorrents(url):
    while True:
        try:
            source = opener.open(URL_BASE + url)
        except:
            print(URL_BASE + url, 'threw an exception')
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
#Main
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


source = opener.open('http://bakabt.com/browse.php?ordertype=size&order=1&limit=100')
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

x = open('ExtractsFree.txt', 'w')
for l in links:
    x.write(URL_BASE + l + '\n')
x.close()
print('Extracted %d links that are freeleech.\nNow getting links to .torrent files' % len(links))

totalToGet = len(links)
torrentFiles = []
for index, link in enumerate(links):
    print('Getting link %d out of %d.        ' % (index + 1, totalToGet), end = '\r')
    torrentFiles.append(getTorrents(link))

print('Got links. Now downloading the files.')
totalToGet = len(torrentFiles)
if not shutil.os.path.exists('BakaBT freeleech'):
    shutil.os.mkdir('BakaBT freeleech')
shutil.os.chdir('BakaBT freeleech')
for index, torrent in enumerate(torrentFiles):
    print('Downloading .torrent %d out of %d.        ' % (index + 1, totalToGet), end = '\r')
    download(torrent)


print('\nDone.')
