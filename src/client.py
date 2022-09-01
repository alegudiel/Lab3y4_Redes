"""
Código del cliente para el servicio de chat.
Ale Gudiel 
Majo Morales 
Marisa Montoya
-------------------------------------------------------
Uso del cliente:
1. Enviar mensaje
2. Actualizar mensajes
3. Eco de mensaje

Algoritmos de envio de mensajes:
1. Flooding
2. Distance Vector
3. Link State

Formato para enviar mensajes:
correoEmisor@alumchat.fun - correoRecipient@alumchat.fun - nodoEmisor - nodoRecipient - saltos - distancia - lista de nodos intermedios - mensaje
"""

# Importar librerías
import asyncio
from datetime import datetime
import slixmpp
import networkx as nx
import ast
from distanceVector import DistanceVector

class Client(slixmpp.ClientXMPP):
    def __init__(self, jid, password, algorithmToUse, nodeE, nodeR, name, graph, graphNx, source):
        super().__init__(jid, password)
        self.received = set()
        self.algorithmToUse = algorithmToUse
        self.nodeE = nodeE
        self.nodeR = nodeR
        # parametros para el distance vector 
        self.name = name
        self.graph = graph
        self.graphNx = graphNx
        self.dvr = DistanceVector(graph, graphNx, source, name)

        # plugins a usar
        self.register_plugin('xep_0030')
        self.register_plugin('xep_0045')

        # manejar la sesión
        self.add_event_handler('session_start', self.start)
        self.add_event_handler('message', self.send_message)

        # manejar los eventos
        self.schedule(name="echo", callback=self.echo_message, repeat=True, seconds=5)
        self.schedule(name="update", callback=self.update_message, repeat=True, seconds=10)
        self.connected_event = asyncio.Event()
        self.presences_received = asyncio.Event()

    #iniciar conexión
    async def start(self, startEvent):
        self.send_presence()
        await self.get_roster()
        self.connected_event.set()

    #uso de mensajeria
    async def send_message(self, messg):
        if messg['type'] in ('normal', 'chat'):
            await self.update_received_messages(messg)

    #eco de mensaje
    def echo_message(self):
        for i in self.nodeR:
            now = datetime.now()
            timestamp = datetime.timestamp(now)
            mensaje = "--" + str(self.jid) + "--" + str(self.name[i]) + "--"+ str(timestamp) +"--" + str(i) + "--"
            self.send_message(
                        mto=self.name[i],
                        mbody=mensaje,
                        mtype='chat' 
                    )

    #actualizar mensajes recibidos
    async def update_received_messages(self, messg):
        message = messg.split('-')

        # usamos el algoritmo flooding
        if message[0] == '1':

            if self.algorithmToUse == '1':
                if message[2] == self.jid:
                    print("Message to self: " +  message[6])
                else:
                    if int(message[3]) > 0:
                        lista = message[4].split(",")
                        if self.nodeE not in lista:
                            message[4] = message[4] + "," + str(self.nodeE)
                            message[3] = str(int(message[3]) - 1)
                            messageString = "-".join(message)
                            for i in self.nodeR:
                                self.send_message(
                                    mto=self.name[i],
                                    mbody=messageString,
                                    mtype='chat' 
                                )  
                    else:
                        pass

            elif self.algorithmToUse == '2':
                if message[2] == self.jid:
                    print("Message to self: " +  message[6])
                else:
                    #enviamos el mensaje por el camino mas corto
                    shortest_neighbor_node = self.dvr.shortest_path(message[2])
                    # al encontrar el camino mas corto, enviamos el mensaje
                    if shortest_neighbor_node: 
                        if shortest_neighbor_node[1] in self.dvr.neighbors:
                            messageString = "-".join(message)
                            self.send_message(
                                mto=message[2],
                                mbody=messageString,
                                mtype='chat' 
                            )
                        else:
                            pass
                    else:
                        pass

            elif self.algorithmToUse == '3':
                if message[2] == self.jid:
                    print("Message to self: " +  message[6])

                else:
                    #enviamos el mensaje por el camino mas corto si no ha pasado por el nodo emisor                    
                    if int(message[3]) > 0:
                        lista = message[4].split(",")
                        if self.nodeE not in lista:
                            message[4] = message[4] + "," + str(self.nodeE)
                            message[3] = str(int(message[3]) - 1)
                            messageString = "-".join(message)
                            target = [x for x in self.graph.nodeR().data() if x[1]["jid"] == message[2]]
                            shortest = nx.shortest_path(self.graph, source=self.nodeE, target=target[0][0])
                            if len(shortest) > 0:
                                self.send_message(
                                    mto=self.name[shortest[1]],
                                    mbody=messageString,
                                    mtype='chat' 
                                )  
                    else:
                        pass
        
        # usamos el algoritmo distance vector
        elif message[0] == '2':
            if self.algorithmToUse == '2':
                esquemaRecibido = message[6]
                
                # si el mensaje es para el nodo emisor, lo ignoramos
                divido = esquemaRecibido.split('-')
                nodos = ast.literal_eval(divido[0])
                aristas = ast.literal_eval(divido[1])
                self.graph.add_nodes_from(nodos)
                self.graph.add_weighted_edges_from(aristas)

                # actualizamos el esquema de distancia
                self.dvr.update_graph(nx.to_dict_of_dicts(self.graph))

                #enviamos el grafo actualizado
                dateFormatNeighbors = self.graph.nodeR().data()
                dataedges = self.graph.edges.data('weight')
                nodesString = str(dateFormatNeighbors) + "-" + str(dataedges)

                for i in self.dvr.neighbors:
                    update_msg = "--" + str(self.jid) + "--" + str(self.name[i]) + "--" + str(self.graph.number_of_nodes()) + "--" + str(self.nodeE) + "--" + nodesString
                    #actualizamos el mensaje para enviarlo a los vecinos
                    self.send_message(
                            mto=self.dvr.name['config'][i],
                            mbody=update_msg,
                            mtype='chat'
                        )
                print("Graph updated")


    def update_message(self):
        if self.algorithmToUse == '2':
            # actualizamos la tabla para el algoritmo distance vector
            dateFormatNeighbors = self.graph.nodeR().data()
            dataedges = self.graph.edges.data('weight')
            nodesString = str(dateFormatNeighbors) + "-" + str(dataedges)

            for i in self.dvr.neighbors:
                update_msg = "--" + str(self.jid) + "--" + str(self.name[i]) + "--" + str(self.graph.number_of_nodes()) + "--" + str(self.nodeE) + "--" + nodesString 
                self.send_message(
                        mto=self.dvr.name[i],
                        mbody=update_msg,
                        mtype='chat'
                    )
            
        elif self.algorithmToUse == '3':
            # actualizamos la tabla para el algoritmo flooding
            dateFormatNeighbors = [x for x in self.graph.nodeR().data() if x[0] in self.nodeR]
            dataedges = [x for x in self.graph.edges.data('weight') if x[1] in self.nodeR and x[0]==self.nodeE]
            nodesString = str(dateFormatNeighbors) + "-" + str(dataedges)
            
            for i in self.nodeR:
                update_msg = "--" + str(self.jid) + "--" + str(self.name[i]) + "--" + str(self.graph.number_of_nodes()) + "--" + str(self.nodeE) + "--" + nodesString
                self.send_message(
                        mto=self.name[i],
                        mbody=update_msg,
                        mtype='chat' 
                    )