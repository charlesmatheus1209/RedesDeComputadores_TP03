from __future__ import print_function
import grpc
import sala_pb2, sala_pb2_grpc
import sys


def envia(msg, dest):
    channel = grpc.insecure_channel(host_port)
    stub = sala_pb2_grpc.SalaStub(channel)
    
    response, call = stub.envia.with_call(sala_pb2.Mensagem_Destino(mensagem=msg,destino=dest), metadata=(("id", id),))
    # print("GRPC client received: " + str(response.resposta))
    print(str(response.resposta))

    channel.close()
    
def lista():
    print("Lista")
    channel = grpc.insecure_channel(host_port)
    stub = sala_pb2_grpc.SalaStub(channel)
    
    response = stub.lista(sala_pb2.Vazio())
    # print("GRPC client received: ")
    print(response.lista_de_resposta)

    channel.close()

def finaliza_registro():
    # print("Finaliza")
    channel = grpc.insecure_channel(host_port)
    stub = sala_pb2_grpc.SalaStub(channel)
    
    response, call = stub.finaliza_registro.with_call(sala_pb2.Identificador(id=id), metadata=(("id", id),))
    print(response)

    channel.close()

def termina():
    # print("termina")
    channel = grpc.insecure_channel(host_port)
    stub = sala_pb2_grpc.SalaStub(channel)
    
    response = stub.termina(sala_pb2.Vazio())
    # print(response)
    channel.close()
    # sys.exit()
    
def registra_entrada():
    # print("registrando a entrada")
    channel = grpc.insecure_channel(host_port)
    stub = sala_pb2_grpc.SalaStub(channel)
    
    response = stub.registra_entrada(sala_pb2.Identificador(id=id))
    # print("registra_entrada -> Resposta: ", response.resposta)
    print(response.resposta)
    
porta = ""
host = ""
id = ""

if(len(sys.argv) == 4):
    # print(sys.argv)
    id = sys.argv[1]
    host = sys.argv[2]
    porta = sys.argv[3]
    host_port = str(host + ":" + porta)
    # print(host_port)
else:
    print("Quantidade de parametros invalida")
    sys.exit()

   
if __name__ == "__main__":
    registra_entrada()
    while(True):
        entrada = input()
        if(entrada != ""):
            comando = entrada[0].upper()
            
            if(comando == 'M'):
                # print("Comando M")
                mensagem = entrada.split(",")[1]
                destino = entrada.split(",")[2]
                envia(mensagem,destino)
            elif(comando == "L"):
                # print("Comando L")
                lista()
            elif(comando == "F"):
                # print("Comando F")
                finaliza_registro()
                break
            elif(comando == "T"):
                # print("Comando T")
                termina()
                