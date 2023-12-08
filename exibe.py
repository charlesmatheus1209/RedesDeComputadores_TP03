import threading
import grpc
import sys
from concurrent import futures

import exibe_pb2, exibe_pb2_grpc
import sala_pb2, sala_pb2_grpc

stopEvent = threading.Event()

class ExibeService(exibe_pb2_grpc.ExibeServicer):    
            
    def termina(self, request, context):
        print("termina")
        stopEvent.set()
        return exibe_pb2.Vazio()

    def exibe(self, request, context):
        # get the string from the incoming request
        message = request.mensagem
        origem = request.origem
        result = f'Sou exibe  e recebi: "{message}" de origem: {origem}'
        print(result)

        return exibe_pb2.MessageResponse(messageResponse = "Recebido por Exibe")


id = ""
porta = ""
hostservidor = ""
portaservidor = ""

if(len(sys.argv) == 5):
    print(sys.argv)
    id = sys.argv[1]
    porta = sys.argv[2]
    hostservidor = sys.argv[3]
    portaservidor = sys.argv[4]
else:
    print("Quantidade de parametros invalida")
    sys.exit()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    exibe_pb2_grpc.add_ExibeServicer_to_server(ExibeService(), server)
    server.add_insecure_port('localhost:8889')
    server.start()
    stopEvent.wait()
    server.stop(None)
    
def registra_saida():
    print("registrando a saida")
    channel = grpc.insecure_channel(hostservidor + ":" + portaservidor)
    stub = sala_pb2_grpc.SalaStub(channel)
    
    response = stub.registra_saida(sala_pb2.RegistroDeSaida(id=id, fqdn="localhost", port=8889))
    print(response.resposta)


if __name__ == '__main__':
    registra_saida()
    serve()