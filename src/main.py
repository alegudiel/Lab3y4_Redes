'''
Código principal del programa.
Ale Gudiel 
Majo Morales 
Marisa Montoya
'''
from client import Client
from aioconsole import ainput
import networkx as nx
from optparse import OptionParser
import yaml

def settings():
    lector_topo = open("src/topo.txt", "r", encoding="utf8")
    lector_names = open("src/names.txt", "r", encoding="utf8")
    topo_string = lector_topo.read()
    names_string = lector_names.read()
    topo_yaml = yaml.load(topo_string, Loader=yaml.FullLoader)
    names_yaml = yaml.load(names_string, Loader=yaml.FullLoader)
    return topo_yaml, names_yaml

def createNodes(topo, names, user):
    for key, value in names['config'].items():
        if user == value:
            return key, topo['config'][key]

def createGraph(topo, names, user):
    graphPlt = {}
    source = None

    for key, value in topo['config'].items():
        graphPlt[key] = {}
        for node in value:
            graphPlt[key][node] = float('inf') # We dont know the weights yet
            if names['config'][node] == user:
                source = node
    
    return graphPlt, source

def graphPlot(topo, names):
    G = nx.DiGraph()
    G.add_nodes_from(G.nodes(data=True))
    G.add_edges_from(G.edges(data=True))

    for key, value in names['config'].items():
            G.add_node(key, jid=value)

    for key, value in topo['config'].items():
        for i in value:
            G.add_edge(key, i, weight=1)

    return G


async def main(xmpp: Client):
    menuOpt = True
    while menuOpt :
        print("""
        --------------------------------------------------------------
        |                                                              |
        |                                                              |
        |                     Welcome to alumchat                      |
        |                                                              |
        |                                                              |
        --------------------------------------------------------------
        1. Send a message
        2. How to use?
        3. Exit
        """)

        menuOpt = int(await ainput("Please select an option: "))

        if menuOpt == 1:
            sendTo = await ainput("With whom do you want to start a chat? ")
            activeChat = True
            while activeChat:
                messg = await ainput("Type your message: ")

                if (messg != 'away') and len(messg) > 0:
                    if xmpp.algoritmo == '1':
                        messg = "--" + str(xmpp.jid) + "--" + str(sendTo) + "--" + str(xmpp.graphPlt.number_of_nodes()) + "--" + str(xmpp.nodo) + "--" + str(messg)
                        for i in xmpp.nodes:
                            xmpp.send_message(
                                mto=xmpp.names[i],
                                mbody=messg,
                                mtype='chat' 
                            )

                    elif xmpp.algoritmo == '2':
                        messg = "--" + str(xmpp.jid) + "--" + str(sendTo) + "--" + str(xmpp.graph.number_of_nodes()) + "--" + str(xmpp.nodo) + "--" + str(messg)
                        shortest_neighbor_node = xmpp.dvr.shortest_path(sendTo)
                        if shortest_neighbor_node: 
                            if shortest_neighbor_node[1] in xmpp.dvr.neighbors:
                                xmpp.send_message(
                                    mto=xmpp.names[shortest_neighbor_node[1]],
                                    mbody=messg,
                                    mtype='chat' 
                                )
                            else:
                                pass
                        else:
                            pass
                        
                    elif xmpp.algoritmo == '3':
                        target = [x for x in xmpp.graph.nodes().data() if x[1]["jid"] == sendTo]
                        messg = "--" + str(xmpp.jid) + "--" + str(sendTo) + "--" + str(xmpp.graph.number_of_nodes()) + "--" + str(xmpp.nodo) + "--" + str(messg)
                        shortest = nx.shortest_path(xmpp.graph, source=xmpp.nodo, target=target[0][0])
                        if len(shortest) > 0:
                            xmpp.send_message(
                                mto=xmpp.names[shortest[1]],
                                mbody=messg,
                                mtype='chat' 
                            )

                    else:
                        xmpp.send_message(
                            mto=sendTo,
                            mbody=messg,
                            mtype='chat' 
                        )

                elif messg == 'away':
                    activeChat = False

        elif menuOpt == 2:
            print("""
            --------------------------------------------------------------
            |                                                              |
            |                                                              |
            |                     How to use alumchat                      |
            |                                                              |
            |                                                              |
            --------------------------------------------------------------
            Algoritmos que se pueden usar:
            1. Flooding
            2. Distance Vector
            3. Link State

            Formato para enviar mensajes:
            correoEmisor@alumchat.fun - correoRecipient@alumchat.fun - nodoEmisor - nodoRecipient - saltos - distancia - lista de nodos intermedios - mensaje
            """)

        else:
            print("""
            --------------------------------------------------------------
            Thank you for using alumchat!
            --------------------------------------------------------------
            """)
            xmpp.disconnect()


if __name__ == '__main__':
    optp = OptionParser()
    optp.add_option('-j', '--jid', dest='jid', help='JID to use')
    optp.add_option('-p', '--password', dest='password', help='password to use')
    optp.add_option('-a', '--algoritmo', dest='algoritmo', help='algoritmo a usar')
    opts, args = optp.parse_args()

    topo, names = settings()

    if opts.jid is None:
        opts.jid = input("Please enter your username - user@alumchat.fun: ")
    if opts.password is None:
        opts.password = input("Please enter your password: ")
    if opts.algoritmo is None:
        opts.algoritmo = input("Please enter the algorithm to use: \n1. Flooding \n2. Distance Vector \n3. Link State \n")

    graphNx, source = createGraph(topo, names, user=opts.jid)
    nodeE, nodeR = createNodes(topo, names, opts.jid)
    graph = graphPlot(topo, names)

    xmpp = Client(opts.jid, opts.password, opts.algoritmo, nodeE, nodeR, names['config'], graph, graphNx, source)
    xmpp.connect()
    xmpp.loop.run_until_complete(xmpp.connected_event.wait())
    xmpp.loop.create_task(main(xmpp))
    xmpp.process(forever=False)