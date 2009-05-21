# -*- coding: utf-8 -*-
from __future__ import with_statement

import sys
from contextlib import closing
from functools import partial

from urllib2 import urlopen
from urllib import urlencode
from urlparse import urlparse, parse_qs

from lxml import etree as ET

FOAF_NS = 'http://xmlns.com/foaf/0.1/'
RDF_NS = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
RDFS_NS = 'http://www.w3.org/2000/01/rdf-schema#'
YAFOAF_NS = 'http://blogs.yandex.ru/schema/foaf/'

ns = {
    'foaf': FOAF_NS,
    'rdf': RDF_NS,
    'rdfs': RDFS_NS,
    'yafoaf': YAFOAF_NS
}

def get_url(url):
    return closing(urlopen(url))

def personurl2login(url):
    host = urlparse(url).netloc.split('.')
    return (host[0] if host[0]!='www' else host[1]).lower()

def cluburl2login(url):
    return urlparse(url).path.split('/')[1].lower()


def get_knows_of(login, page_arg, url2login):
    def get_impl(login, page):
        friends = []
        url = "http://%s.ya.ru/foaf.xml?%s=%d" % (login, page_arg, page)
        with get_url(url) as fd:
            tree = ET.parse(fd)
            for _, knows in ET.iterwalk(tree, tag='{%(foaf)s}knows' % ns):
                friends += [url2login(p.get('{%(rdf)s}resource' % ns)) for p in knows.findall('.//{%(rdfs)s}seeAlso' % ns)]
            next_page = None
            for url in [s.get('{%(rdf)s}resource' % ns) for s in tree.findall('{%(foaf)s}Person/{%(rdfs)s}seeAlso' % ns)]:
                qs = parse_qs(urlparse(url).query)
                if page_arg in qs:
                    next_page = int(qs[page_arg][0])

        return friends, next_page

    friends = []
    page = 0
    while page is not None:
        new_friends, page = get_impl(login, page)
        friends += new_friends

    return friends

get_friends_of = partial(get_knows_of, page_arg='p', url2login = personurl2login)
get_clubs_of = partial(get_knows_of, page_arg='clubs', url2login = cluburl2login)

YA_USER='<ya user="%s"/>'
YA_CLUB='<ya club="%s"/>'

def intersect(func, l1, l2, print_tmpl):
    k_l1 = func(l1)
    k_l2 = func(l2)
    isec = set.intersection(set(k_l1), set(k_l2))
    print "%s[%d] ∩ %s[%d] ⇢ %d" % (YA_USER % l1, len(k_l1), YA_USER % l2, len(k_l2), len(isec))
    print ", ".join([print_tmpl % k for k in isec])


if __name__ == '__main__':
    l1, l2 = sys.argv[1], sys.argv[2]
    print "<h3>друзья</h3>"
    intersect(get_friends_of, l1, l2, '<ya user="%s"/>')
    print "<h3>клубы</h3>"
    intersect(get_clubs_of, l1, l2, '<ya club="%s"/>')




