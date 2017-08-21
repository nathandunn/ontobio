from ontobio.ontol_factory import OntologyFactory
from ontobio.lexmap import LexicalMapEngine
import networkx as nx
import logging

def test_lexmap_basic():
    """
    Text lexical mapping
    """
    factory = OntologyFactory()
    print("Creating ont")
    ont = factory.create('tests/resources/lexmap_test.json')
    lexmap = LexicalMapEngine()

    lexmap.index_ontology(ont)

    print(lexmap.lmap)
    print(ont.all_synonyms())
    g = lexmap.get_xref_graph()
    for x,y,d in g.edges_iter(data=True):
        print("{}<->{} :: {}".format(x,y,d))
    for x in g.nodes():
        print("{} --> {}".format(x,lexmap.grouped_mappings(x)))
    assert g.has_edge('Z:2','ZZ:2') # roman numerals
    assert g.has_edge('Z:2','Y:2')  # case insensitivity
    assert g.has_edge('A:1','B:1')  # synonyms
    assert g.has_edge('B:1','A:1')  # bidirectional
    for x,y,d in g.edges_iter(data=True):
        print("{}<->{} :: {}".format(x,y,d))
        cpr = d[lexmap.CONDITIONAL_PR]
        assert cpr > 0 and cpr <= 1.0

    lexmap = LexicalMapEngine(config=dict(normalized_form_confidence=0.25))
    ont.add_node('TEST:1', 'foo bar')
    ont.add_node('TEST:2', 'bar foo')
    lexmap.index_ontology(ont)
    g = lexmap.get_xref_graph()
    assert g.has_edge('TEST:1','TEST:2') # normalized
    assert round(g['TEST:1']['TEST:2']['score']) == 25
    
    
def test_lexmap_multi():
    """
    Text lexical mapping
    """
    factory = OntologyFactory()
    print("Creating ont")
    files = ['x','m','h','bto']
    onts = [factory.create('tests/resources/autopod-{}.json'.format(f)) for f in files]
    lexmap = LexicalMapEngine()
    lexmap.index_ontologies(onts)
    #print(lexmap.lmap)
    #print(ont.all_synonyms())
    g = lexmap.get_xref_graph()
    for x in g.nodes():
        print("{} --> {}".format(x,lexmap.grouped_mappings(x)))
    for x,y,d in g.edges_iter(data=True):
        cl = nx.ancestors(g,x)
        print("{} '{}' <-> {} '{}' :: {} CLOSURE={}".format(x,lexmap.label(x),y,lexmap.label(y),d,len(cl)))
        cpr = d[lexmap.CONDITIONAL_PR]
        assert cpr > 0 and cpr <= 1.0
    unmapped = lexmap.unmapped_nodes(g)
    print('U: {}'.format(len(unmapped)))
    unmapped = lexmap.unmapped_nodes(g, rs_threshold=4)
    print('U4: {}'.format(len(unmapped)))

    