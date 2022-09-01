'''
Código principal del programa.
Ale Gudiel 
Majo Morales 
Marisa Montoya
'''
from client import Client
from aioconsole import ainput
import networkx as nx
import getpass
from optparse import OptionParser
import yaml

def settings():
    lector_topo = open("./topo.txt", "r", encoding="utf8")
    lector_names = open("./names.txt", "r", encoding="utf8")
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
    graph = {}
    source = None

    for key, value in topo['config'].items():
        graph[key] = {}
        for node in value:
            graph[key][node] = float('inf') # We dont know the weights yet
            if names['config'][node] == user:
                source = node
    
    return graph, source

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


# Funcion para manejar el cliente
async def main(xmpp: Client):
    corriendo = True
    # print(xmpp.topo)
    # print(xmpp.names)
    # Cambio en vez de pasarle toda la red solo los nodos conectados
    #print(xmpp.nodo)
    #print(xmpp.nodes)
    while corriendo:
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
        opcion = await ainput("Please select an option: ")
        if opcion == '1':
            destinatario = await ainput("With whom do you want to start a chat? ")
            activo = True
            while activo:
                mensaje = await ainput("Type your message: ")
                if (mensaje != 'volver') and len(mensaje) > 0:
                    if xmpp.algoritmo == '1':
                        mensaje = "--" + str(xmpp.jid) + "--" + str(destinatario) + "--" + str(xmpp.graph.number_of_nodes()) + "||" + str(xmpp.nodo) + "--" + str(mensaje)
                        for i in xmpp.nodes:
                            xmpp.send_message(
                                mto=xmpp.names[i],
                                mbody=mensaje,
                                mtype='chat' 
                            )
                    elif xmpp.algoritmo == '2':
                        # Enviar el mensaje por la ruta mas corta
                        mensaje = "--" + str(xmpp.jid) + "--" + str(destinatario) + "--" + str(xmpp.graph.number_of_nodes()) + "||" + str(xmpp.nodo) + "--" + str(mensaje)
                        shortest_neighbor_node = xmpp.dvr.shortest_path(destinatario)
                        if shortest_neighbor_node: # If we have a path
                            if shortest_neighbor_node[1] in xmpp.dvr.neighbors: # And is in our neighbors list
                                # We send the message
                                xmpp.send_message(
                                    mto=xmpp.names[shortest_neighbor_node[1]],
                                    mbody=mensaje,
                                    mtype='chat' 
                                )
                            else:
                                pass
                        else:
                            pass

                    elif xmpp.algoritmo == '3':
                        target = [x for x in xmpp.graph.nodes().data() if x[1]["jid"] == destinatario]
                        mensaje = "--" + str(xmpp.jid) + "--" + str(destinatario) + "--" + str(xmpp.graph.number_of_nodes()) + "||" + str(xmpp.nodo) + "--" + str(mensaje)
                        shortest = nx.shortest_path(xmpp.graph, source=xmpp.nodo, target=target[0][0])
                        if len(shortest) > 0:
                            xmpp.send_message(
                                mto=xmpp.names[shortest[1]],
                                mbody=mensaje,
                                mtype='chat' 
                            )
                    else:
                        xmpp.send_message(
                            mto=destinatario,
                            mbody=mensaje,
                            mtype='chat' 
                        )
                elif mensaje == 'volver':
                    activo = False
                else:
                    pass
        elif opcion == '2':
            corriendo = False
            xmpp.disconnect()
        else:
            pass



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
        opts.password = getpass.getpass("Please enter your password: ")
    if opts.algoritmo is None:
        opts.algoritmo = input("Please enter the algorithm to use: \n1. Flooding \n2. Distance Vector \n3. Link State \n")

    graph_dict, source = createGraph(topo, names, user=opts.jid)
    nodo, nodes = createNodes(topo, names, opts.jid)
    graph = graphPlot(topo, names)

    xmpp = Client(opts.jid, opts.password, opts.algoritmo, nodo, nodes, names['config'], graph, graph_dict, source)
    xmpp.connect()
    xmpp.loop.run_until_complete(xmpp.connected_event.wait())
    xmpp.loop.create_task(main(xmpp))
    xmpp.process(forever=False)