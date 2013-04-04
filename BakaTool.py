#Uses your cookies to search BakaBT for torrents that are freeleech
#Possible features: Small torrents only

import sys
import argparse
from miscutil import *

def get_arg_parser():
    parser = argparse.ArgumentParser(description='Small tool to extend '
                                     + 'search capabilities of BakaBT '
                                     + 'anime tracker.')
    parser.add_argument('-u', '--username', required=True,
                        help='Site username.')
    parser.add_argument('-p', '--password', required=True,
                        help='Site password')
    parser.add_argument('-b', '--bonus', action='store_true', default=False,
                       help='Only get bonus torrents')
    parser.add_argument('-n', '--no-freeleech',
                        action='store_false', default=True,
                        help='Do not restrict results to freeleech torrents')
    parser.add_argument('-d', '--directory', default='downloads',
                        help='Download directory (default=downloads)')
    parser.add_argument('-l', '--limit', nargs=1, default=5,
                        help='Maximum number of pages (default=5)')
    parser.add_argument('-a', '--amount', nargs=1, default=20,
                        help='Torrents per page, max 100 (default=20)')
    parser.add_argument('-s', '--smallest', action='store_true', default=False,
                        help='Sort torrents by their size (default=False)')
    parser.add_argument('-w', '--website', default='http://bakabt.me',
                        help='Site to use (default=http://bakabt.me)')
    parser.add_argument('-t', '--timeout', default=[15.0], type=float,
                        help='Timeout for any URL request (default=15.0s)')

    return parser


def main():
    conf = get_arg_parser().parse_args()


    status = liftM(concat, (login(conf) >> get_pages(conf)).bind(
        lambda x: mapE(
            lambda y: liftM(get_links(conf),
                            get_page_source(conf)(y)), x))).bind(
                lambda z: map(klesli_comp(
                    download(conf), get_torrent_url(conf)), z))

    sys.stdout.write('%s\n' % status)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
