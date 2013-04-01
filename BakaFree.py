#Uses your cookies to search BakaBT for torrents that are freeleech
#Possible features: Small torrents only

import sys
from miscutil import *

URL_BASE = 'http://bakabt.me'

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

    m_links = mapMaybe(mKlesliComp(getLinks, get_page_source),
                       get_pages(limit=2))

    if m_links.is_nothing():
        sys.stderr.write('Got Nothing in the end.\n')
        sys.exit(3)

    all_links = [ y for x in m_links.get_value() for y in x ]
    urls = [ get_torrent_url(link) for link in all_links ]
    print urls

    num_links = len(urls)
    x = 1
    for link in urls:
        sys.stdout.write('Downloading %d/%d\n' % (x, num_links))
        download(link)
        x += 1


if __name__ == '__main__':
    main()
