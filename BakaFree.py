#Uses your cookies to search BakaBT for torrents that are freeleech
#Possible features: Small torrents only

import sys
import re
import shutil
import socket
import mechanize

URL_BASE = 'http://bakabt.me'
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


def search(word):
    request = mechanize.Request('%s/browse.php?q=%s' % (URL_BASE, word))
    response = mechanize.urlopen(request)
    return response.read()



def main():
    if len(sys.argv) != 3:
        sys.stdout.write("usage: python BakaFree.py USERNAME PASSWORD")
        sys.exit(2)

    logged_in = login(sys.argv[1], sys.argv[2])

    if logged_in:
        sys.stdout.write('Successfully logged in as %s\n' % sys.argv[1] )
    else:
        sys.stdout.write('Failed to log in.\n')
        sys.exit(3)


def login(username, password):
    request = mechanize.Request('%s/login.php' % URL_BASE)
    response = mechanize.urlopen(request)
    forms = mechanize.ParseResponse(response)
    response.close()

    form = forms[2]
    form['username'] = username
    form['password'] = password
    login_request = form.click()
    try:
        login_response = mechanize.urlopen(login_request)
    except mechanize.HTTPError, login_response:
        sys.stdout.write('HTTPError when logging in...\n')

    return login_response.geturl() == ('%s/index.php' % URL_BASE)

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
