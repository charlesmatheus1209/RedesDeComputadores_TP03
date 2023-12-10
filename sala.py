import socket
import sys
import threading
import grpc
import json
from concurrent import futures

import sala_pb2, sala_pb2_grpc
import exibe_pb2, exibe_pb2_grpc

ip_local = 0
    
stopEvent = threading.Event()

class SalaService(sala_pb2_grpc.SalaServicer):    
    registros_de_entrada_salvos = list()
    registros_de_saida_salvos = list()
        
    def registra_entrada(self, request, context):
        # print("registra_entrada")
        if(request.id in self.registros_de_entrada_salvos):
            # print(f"Já contem {request.id}")
            return sala_pb2.NumeroResposta(resposta = -1)
        else:
            self.registros_de_entrada_salvos.append(request.id)
            # print("Inserindo: ", self.registros_de_entrada_salvos)
            return sala_pb2.NumeroResposta(resposta = len(self.registros_de_entrada_salvos))
    
    def registra_saida(self, request, context):
        # print("registra_saida")
        identificadores = list()
        
        for index in range(len(self.registros_de_saida_salvos)):
            identificadores.append(self.registros_de_saida_salvos[index][0])
                    
        if (request.id in identificadores):
            # print("Já existe esse exibidor")
            return sala_pb2.NumeroResposta(resposta = -1)
        else:
            # print(request.id, request.fqdn, request.port)
            
            self.registros_de_saida_salvos.append((request.id, request.fqdn, request.port))
            # print(self.registros_de_saida_salvos)
            return sala_pb2.NumeroResposta(resposta = len(self.registros_de_saida_salvos))
               
    def lista(self, request, context):
        # print("lista")
        return sala_pb2.ListaResposta(lista_de_resposta = self.registros_de_entrada_salvos)

    def finaliza_registro(self, request, context):
        # print(f"finaliza_registro: {request.id}")
        _id = ""
        for chave, valor in context.invocation_metadata():  
            if chave == "id":
                _id = valor
        
        # print("IIIIIDDDDD", _id)
        
        if(_id in self.registros_de_entrada_salvos):
            # print(f"Removendo:  {request.id}")
            self.registros_de_entrada_salvos.remove(_id)
            indexes = []
            i = 0
            for index in range(len(self.registros_de_saida_salvos)):
                if(self.registros_de_saida_salvos[index][0] == _id):
                    i += 1
                    channel = grpc.insecure_channel(f"{self.registros_de_saida_salvos[index][1]}:{self.registros_de_saida_salvos[index][2]}")
                    stub = exibe_pb2_grpc.ExibeStub(channel)
                    
                    response = stub.termina(exibe_pb2.Vazio())
                    # print(response)

                    channel.close()
                    indexes.append(index)
            
            for i in range(len(indexes)):
                self.registros_de_saida_salvos.pop(i)
            if i == 0:
                return sala_pb2.NumeroResposta(resposta = 0)
            else:
                return sala_pb2.NumeroResposta(resposta = 1)
        else:
            return sala_pb2.NumeroResposta(resposta = -1)
        
    def termina(self, request, context):
        # print("termina")

        for index in range(0,len(self.registros_de_saida_salvos)):
            # print(index)
            # print(self.registros_de_saida_salvos[index][1] + ":" + str(self.registros_de_saida_salvos[index][2]))
            channel = grpc.insecure_channel(self.registros_de_saida_salvos[index][1] + ":" + str(self.registros_de_saida_salvos[index][2]))
            stub = exibe_pb2_grpc.ExibeStub(channel)
            
            stub.termina(exibe_pb2.Vazio())
            
            channel.close()
            
        
        stopEvent.set()
        return sala_pb2.Vazio()

    def envia(self, request, context):
        _id = ""
        for chave, valor in context.invocation_metadata():  
            if chave == "id":
                _id = valor
        
        # print("IIIIIDDDDD", _id)
        
        numero_de_envios = 0
        # get the string from the incoming request
        message = request.mensagem
        destino = request.destino
        result = f'Sou a sala e recebi: "{message}", para destino "{destino}"'
        
        if(destino == "todos"):
            for index in range(len(self.registros_de_saida_salvos)):
                # print(f"{self.registros_de_saida_salvos[index][1]}:{self.registros_de_saida_salvos[index][2]}")
                channel = grpc.insecure_channel(f"{self.registros_de_saida_salvos[index][1]}:{self.registros_de_saida_salvos[index][2]}")
                
                stub = exibe_pb2_grpc.ExibeStub(channel)
                response = stub.exibe(exibe_pb2.Mensagem_Origem(mensagem=message,origem=_id))
                # print("GRPC client received: " + response.messageResponse)

                channel.close()
                numero_de_envios += 1
        else:
            for index in range(len(self.registros_de_saida_salvos)):
                if(self.registros_de_saida_salvos[index][0] == destino):
                    # print(self.registros_de_saida_salvos[index][1] + ":" + str(self.registros_de_saida_salvos[index][2]))
                    channel = grpc.insecure_channel(f"{self.registros_de_saida_salvos[index][1]}:{self.registros_de_saida_salvos[index][2]}")
                    stub = exibe_pb2_grpc.ExibeStub(channel)
                    
                    response = stub.exibe(exibe_pb2.Mensagem_Origem(mensagem=message,origem=str(socket.gethostbyname(socket.gethostname()))))
                    # print("GRPC client received: " + response.messageResponse)

                    channel.close()
                    numero_de_envios += 1
        
        # print(result)
        
        return sala_pb2.NumeroResposta(resposta = numero_de_envios)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sala_pb2_grpc.add_SalaServicer_to_server(SalaService(), server)
    # print(socket.getfqdn() + ':' + str(porta))
    server.add_insecure_port(socket.getfqdn() + ':' + str(porta))
    server.start()
    stopEvent.wait()
    server.stop(None)

porta = ""

if(len(sys.argv) == 2):
    # print(sys.argv)
    porta = sys.argv[1]
else:
    print("Quantidade de parametros invalida")
    sys.exit()


if __name__ == '__main__':
    serve()