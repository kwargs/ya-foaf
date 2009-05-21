# -*- coding: utf-8 -*-
from __future__ import with_statement

from contextlib import closing
from collections import defaultdict
import sys

from get_friends_of import get_friends_of

import logging 
import pickle
logging.basicConfig(level = logging.DEBUG, stream=sys.stdout)
log = logging.getLogger()

def get_file(fname, mode='r'):
    return closing(open(fname, mode))

def write_data(gr, user):
    with get_file('cache/sc-%s.pickle' % user, 'w') as fd:
        pickle.dump(gr, fd)

def read_data(user):
    try:
        with get_file('cache/sc-%s.pickle' % user, 'r') as fd:
            return pickle.load(fd)
    except (IOError, EOFError):
        return None

def second_circle(user):
    sc = read_data(user)
    if sc is None:
        sc = {}
        log.debug("try read '%s' first circle" % user)
        first_circle = set(get_friends_of(user))

        for friend in first_circle:
            log.debug("processing knows: '%s' " % friend)
            for f_of_f in get_friends_of(friend):
                if f_of_f not in first_circle and f_of_f != user:
                    sc[f_of_f] = sc.get(f_of_f, 0) + 1
        write_data(sc, user)

    return sc


if __name__ == '__main__':
    user = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv)>2 else 10

    sc = second_circle(user).items()
    print "всего во 2-ом круге: ", len(sc)
    popular = filter(lambda x:x[1]>limit, sc)
    popular.sort(lambda x, y:cmp(x[1], y[1]), reverse=True)
    print "популярные с весом не меньше %d - %d" % (limit + 1, len(popular))
    p_dict = defaultdict(list)
    for login, w in popular:
        p_dict[w].append(login)

    for w in sorted(p_dict.keys(), reverse=True):
        s = ', '.join(['<ya user="%s"/>' % p for p in p_dict[w]])
        print '%d %s' % (w, s)










