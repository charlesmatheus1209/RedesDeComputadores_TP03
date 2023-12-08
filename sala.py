import sys
import grpc
from concurrent import futures

import sala_pb2, sala_pb2_grpc
import exibe_pb2, exibe_pb2_grpc


class SalaService(sala_pb2_grpc.SalaServicer):    
    registros_de_entrada_salvos = list()
    registros_de_saida_salvos = list()
    
    def registra_entrada(self, request, context):
        print("registra_entrada")
        if(request.id in self.registros_de_entrada_salvos):
            print(f"Já contem {request.id}")
            return sala_pb2.NumeroResposta(resposta = -1)
        else:
            self.registros_de_entrada_salvos.append(request.id)
            print("Inserindo: ", self.registros_de_entrada_salvos)
            return sala_pb2.NumeroResposta(resposta = len(self.registros_de_entrada_salvos))
    
    def registra_saida(self, request, context):
        print("registra_saida")
        
        identificadores = list()
        
        for index in range(len(self.registros_de_saida_salvos)):
            identificadores.append(self.registros_de_saida_salvos[index][0])
            
        print(identificadores)
        if (request.id in identificadores):
            print("Já existe esse exibidor")
            return sala_pb2.NumeroResposta(resposta = -1)
        else:
            self.registros_de_saida_salvos.append((request.id, request.fqdn, request.port))
            return sala_pb2.NumeroResposta(resposta = len(self.registros_de_saida_salvos))        
    
    def lista(self, request, context):
        print("lista")
        return sala_pb2.ListaResposta(lista_de_resposta = self.registros_de_entrada_salvos)

    def finaliza_registro(self, request, context):
        print("finaliza_registro")
        return sala_pb2.NumeroResposta(resposta = 0)
        
    def termina(self, request, context):
        print("termina")
        
        return sala_pb2.Vazio()

    def envia(self, request, context):
        # get the string from the incoming request
        message = request.mensagem
        destino = request.destino
        
        # print(context.details.)
        
        print(f"Envia --- Mensagem: {message} Destino: {destino}")
        print(self.registros_de_saida_salvos)
        if(destino == "todos"):
            print("Tenho que enviar para todos os exibidores")
            for index in range(len(self.registros_de_saida_salvos)):
                channel = grpc.insecure_channel(self.registros_de_saida_salvos[index][1] + ":" + str(self.registros_de_saida_salvos[index][2]))
                stub = exibe_pb2_grpc.ExibeStub(channel)
                
                response = stub.exibe(exibe_pb2.Mensagem_Origem(mensagem=message,origem="teste"))
                print("Resposta do Exibe: " + response.messageResponse)

                channel.close()
        else:
            print(f"Enviando mensagem apenas para {destino}")
        
            for index in range(len(self.registros_de_saida_salvos)):
                if(self.registros_de_saida_salvos[index][0] == destino):
                    channel = grpc.insecure_channel(self.registros_de_saida_salvos[index][1] + ":" + str(self.registros_de_saida_salvos[index][2]))
                    stub = exibe_pb2_grpc.ExibeStub(channel)
                    
                    response = stub.exibe(exibe_pb2.Mensagem_Origem(mensagem=message,origem="teste"))
                    print("Resposta do Exibe: " + response.messageResponse)

                    channel.close()
        
        
        
        print(self.registros_de_saida_salvos)

        return sala_pb2.MessageResponse(messageResponse = "Recebido")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sala_pb2_grpc.add_SalaServicer_to_server(SalaService(), server)
    server.add_insecure_port('localhost:'+ str(porta))
    server.start()
    server.wait_for_termination()

porta = ""

if(len(sys.argv) == 2):
    print(sys.argv)
    porta = sys.argv[1]
else:
    print("Quantidade de parametros invalida")
    sys.exit()


if __name__ == '__main__':
    serve()