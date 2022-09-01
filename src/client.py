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
        # falta declarar el self.dvr para el algoritmo distance vector, debemos enviar los parametros de graph, graphNx, source y name

        # plugins a usar
        self.register_plugin('xep_0030')
        self.register_plugin('xep_0045')

        # manejar la sesión
        self.add_event_handler('session_start', self.start)
        self.add_event_handler('message', self.message)

        # manejar los eventos
        self.schedule(name="echo", callback=self.echo_message, recurring=True, seconds=5)
        self.schedule(name="update", callback=self.update_messages, recurring=True, seconds=10)
        self.connected_event = asyncio.Event()
        self.presences_received = asyncio.Event()

    #iniciar conexión
    async def connect(self, startEvent):
        self.send_presence()
        self.get_roster()
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

    