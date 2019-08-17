import json

import networkx as nx
import pydot
import matplotlib.pyplot as plt
import pylab


def fromDotToGraph(filename):
    tmp = nx.drawing.nx_pydot.read_dot(filename)
    G = nx.Graph(tmp)
    return G


def save(G, fname):
    fh = open(fname, 'wb')
    nx.write_multiline_adjlist(G, fh)


def load(fname):
    G = nx.read_multiline_adjlist(fname)
    return G


# def CLA(G):
#     lst = nx.all_pairs_lowest_common_ancestor(G)
#     print(lst)
#     print("a")

def uniq(lst):
    uniq = set()
    for i in lst:  # O(n), n=|l|
        if not (i in uniq or tuple([i[1], i[0]]) in uniq):  # O(1)-Hashtable

            uniq.add(i)
    return list(uniq)


def getGraphOfNet(path):
    G = load(path)
    return G


def loadAndSaveGtoJson(fileName):
    G = fromDotToGraph("./Model_European_System/europe.dot")
    save(G, "./Model_European_System/savedGraphEurope.adjlist")


def convertToDirectedGraph(G):
    H = G.to_directed()
    lstEven = uniq(H.edges)
    # lstEven = [v for i, v in enumerate(lst) if i % 2 == 0]
    # print(list(H.edges))
    # print(lstEven)
    T = nx.DiGraph()
    T.add_edges_from(lstEven)
    # write_dot(T, "europeanTreeGraph.dot")
    return T


def getCLABetweenPair(G, n1, n2):
    return nx.lowest_common_ancestor(G, n1, n2)


def getPathLenBetweenNodes(G, n1, n2):
    p = nx.shortest_path_length(G, source=n1, target=n2)
    return p


# input: networks dot file and analytics file, output: colored graph
def draw(dotFile, analyticsFile, pathToGraphImage):
    graph = pydot.graph_from_dot_file(dotFile)
    out_of_range_nodes = analyticsFile.get('UNDER_VOLTAGE_NODES').keys()
    all_nodes = analyticsFile.get('NODES').keys()
    for badNode in out_of_range_nodes:
        #bad_values_for_node = str(analyticsFile['UNDER_VOLTAGE_NODES'][badNode])
        graph[0].add_node(pydot.Node(badNode, color='red', fillcolor='red', style='filled'))
    for node in all_nodes:
        if node not in out_of_range_nodes:
            graph[0].add_node(pydot.Node(node, color='green', fillcolor='green', style='filled'))
    graph[0].write_png(pathToGraphImage)

def save_graph(graph,file_name):
    #initialze Figure
    plt.figure(num=None, figsize=(20, 20), dpi=80)
    plt.axis('off')
    fig = plt.figure(1)
    pos = nx.spring_layout(graph)
    nx.draw_networkx_nodes(graph,pos)
    nx.draw_networkx_edges(graph,pos)
    nx.draw_networkx_labels(graph,pos)

    cut = 1.00
    xmax = cut * max(xx for xx, yy in pos.values())
    ymax = cut * max(yy for xx, yy in pos.values())
    plt.xlim(0, xmax)
    plt.ylim(0, ymax)
    plt.show()
    plt.savefig(file_name,bbox_inches="tight")
    pylab.close()
    del fig

# def DrawTree(G):
#     plt.title('draw_networkx')
#     pos =  graphviz_layout(G, prog='dot')
#     nx.draw(G, pos, with_labels=False, arrows=False)
#     plt.savefig('nx_test.png')


def Agraph(G):
    pos = nx.spring_layout(G)
    plt.figure(figsize=(20, 20))
    nx.draw(G, pos=pos, arrows=False, node_color='black', width=0.7, alpha=0.9)
    plt.show()
#Assuming that the graph g has nodes and edges entered
# save_graph(g,"my_graph.pdf")

#it can also be saved in .svg, .png. or .ps formats

# G = nx.read_multiline_adjlist("savedGraphEurope.json")

#save_graph(G,"testG.png")
# DrawTree(convertToDirectedGraph(G))
# Agraph(G)

####################### TESTING
# with open('totalMap.json') as json_file:
#     data = json.load(json_file)
#     draw('europeanTreeGraph.dot',data,'newpic.png')
# dot -Tpng europe.dot > output.png
# ruby glm2dot.rb path/to/example_in.glm path/to/example_out.dot
