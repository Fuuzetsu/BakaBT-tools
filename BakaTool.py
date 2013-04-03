#Uses your cookies to search BakaBT for torrents that are freeleech
#Possible features: Small torrents only

import sys
import argparse
from miscutil import *

URL_BASE = 'http://bakabt.me'

def get_arg_parser():
    parser = argparse.ArgumentParser(description='Small tool to extend '
                                     + 'search capabilities of BakaBT '
                                     + 'anime tracker.')
    parser.add_argument('-u', '--username', nargs=1, required=True,
                        help='Site username.')
    parser.add_argument('-p', '--password', nargs=1, required=True,
                        help='Site password')
    parser.add_argument('-b', '--bonus', action='store_true', default=False,
                       help='Only get bonus torrents')
    parser.add_argument('-n', '--no-freeleech',
                        action='store_false', default=True,
                        help='Do not restrict results to freeleech torrents')
    parser.add_argument('-d', '--directory', nargs=1, default='downloads',
                        help='Download directory (default=downloads)')

    return parser


def main():
    conf = get_arg_parser().parse_args()

    status = liftM(concat, (login(conf.username[0], conf.password[0])
                                      >> get_pages(limit=2)).bind(
        lambda x: mapE(
            lambda y: liftM(get_links, get_page_source(y)), x))).bind(
                lambda z: map(klesli_comp(download(conf), get_torrent_url), z))

    sys.stdout.write('%s\n' % status)

if __name__ == '__main__':
    main()
