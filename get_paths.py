# -*- coding: utf-8 -*-
from __future__ import with_statement

from contextlib import closing
import codecs
import sys

import networkx as NX
import pylab

from get_friends_of import get_friends_of

import logging 
logging.basicConfig(level = logging.DEBUG, stream=sys.stdout)
log = logging.getLogger()

def edgelist_fname(from_user, to_user, **kw):
    names = [from_user, to_user]; names.sort()
    return 'edgelist-%s-to-%s.utf-8' % tuple(names)

def get_file(fname, mode='r'):
    return closing(open(fname, mode))

def write_graph(gr, from_user, to_user):
    with get_file(edgelist_fname(**locals()), 'w') as fd:
        NX.write_multiline_adjlist(gr, fd, delimiter='\t')

def read_graph(from_user, to_user):
    try:
        with get_file(edgelist_fname(**locals()), 'r') as fd:
            return NX.read_multiline_adjlist(fd, delimiter='\t')
    except IOError:
        return None

def build_graph(from_user, to_user):

    def add_person_circle(gr, person, passed_persons):
        log.debug("try read '%s' circle" % person)
        for knows in get_friends_of(person):
            log.debug("processing knows: '%s' " % knows)
            gr.add_edge(person.encode('utf-8'), knows.encode('utf-8'))
            if knows not in passed_persons:
                for knows_knows in get_friends_of(knows):
                    gr.add_edge(knows.encode('utf-8'), knows_knows.encode('utf-8'))
                passed_persons.add(knows)
        passed_persons.add(person)

    gr = read_graph(from_user, to_user)
    if gr is None:
        gr = NX.DiGraph()
        passed_persons = set()
        add_person_circle(gr, from_user, passed_persons)
        add_person_circle(gr, to_user, passed_persons)
        write_graph(gr, from_user, to_user)

    return gr

def simplify(gr, from_user, to_user):
    for n in [i for i in gr]:
        if not gr.degree(n)>1:
            gr.delete_node(n)
    for n in [i for i in gr]:
        if not (gr.has_edge(from_user, n) or gr.has_edge(to_user, n)):
            gr.delete_node(n)
    return gr


def draw(graph, from_user, to_user):
    pylab.figure(figsize=(10,10))

    pos = NX.spring_layout(graph, iterations=10)#NX.spring_layout(graph)

    NX.draw_networkx_nodes(
        graph,
        pos,
        with_labels=True,
        alpha=0.5,
        node_size=[graph.degree(n)*10 for n in graph]
    )

    NX.draw_networkx_edges(
        graph,
        pos,
        alpha=0.3
    )

    pylab.xticks([])
    pylab.yticks([])
    pylab.savefig(edgelist_fname(from_user, to_user)+'.png')

if __name__ == '__main__':
    from_user, to_user = sys.argv[1], sys.argv[2]
    gr = build_graph(from_user, to_user)
    log.debug("orig node count: %d" % len(gr))
    gr = simplify(gr, from_user, to_user)
    log.debug("simplify node count: %d" % len(gr))
    draw(gr, from_user, to_user)











