#  Implementação de um chat básico:
#  ○ Deve ter no mínimo 3 clientes;
#  ○ Deverá ter dois códigos diferentes, o do servidor e do cliente;
#  ○ O Cliente terá um menu onde ele irá escolher o que ele deseja fazer:
# ■ Escutar até receber uma mensagem, depois ele volta para o menu;
#  ■ Apenas escutar mensagens e mostrar na tela;
#  ■ Sair.
#  ■ Mandar mensagem para 1 cliente informando a qual cliente que ele deseja mandar a
# mensagem;
#  ■ Enviar mensagem e escutar a resposta e depois voltar ao menu;
#  ○ O servidor deverá censurar mensagens indevidas (as palavras são definidas pelo grupo).
#  ○ Caso o cliente mande 3 mensagens indevidas no período de 1 minuto, ele deve ser banido e as
# mensagens dele não serão mais transmitidas.
import socket
import threading
import json

BUFFER = 1024
HOST = "192.168.1.15"
PORT = 9000
NMR_CLIENTES = 1000
class Cliente:
    def __init__(self, cliente_socket, cliente_addrs,user_name) -> None:
        self.cliente_socket: socket.socket = cliente_socket
        self.cliente_addrs = cliente_addrs
        self.name = user_name

class Servidor:

    def __init__(self):
        self.addr = (HOST, PORT)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._clientes: dict[str, Cliente] = {}

    def init(self):
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(self.addr)
        self.server_socket.listen(NMR_CLIENTES)

    @property
    def clientes(self):
        return self._clientes

    def is_suport_connect(self):
        is_ok = True
        if len(self.clientes) >= NMR_CLIENTES:
            is_ok = False
        return is_ok

    def __add_clientes(self, cliente_addrs, cliente_socket, user_name) -> bool:
        is_add = True
        if user_name in self.clientes:
            is_add = False
        else:
            self.clientes[user_name] = Cliente(cliente_socket, cliente_addrs,user_name)
        return is_add

    def thread_connect_user(self):
        while True:
            client_socket, client_addr = self.server_socket.accept()
            name = client_socket.recv(BUFFER).decode()

            if not self.is_suport_connect():
                client_socket.send("disconnected: Servidor cheio!".encode())
                client_socket.close()

            else:
                if not (self.__add_clientes(client_addr, client_socket, name)):
                    client_socket.send("disconnected: Nome em uso!".encode())
                    client_socket.close()
                else:
                    print(f"Cliente {name} conectado.")
                    client_socket.send("connected: conectado!".encode())
                    threading.Thread(target=self.handle_client, args=(self.clientes[name], name)).start()

    def handle_client(self, cliente_send: Cliente, name_send):
        try:
            msg_recebida: str = cliente_send.cliente_socket.recv(BUFFER).decode()
            msg_recebida = json.loads(msg_recebida)
            
            msg_recebida = msg_recebida["produto"]
            
            print(msg_recebida)
            
        except socket.timeout:
            print(f"Tempo limite excedido para o cliente {cliente_send.cliente_addrs}.")

        except (ConnectionResetError, ConnectionAbortedError):
            print(f"Cliente {cliente_send.cliente_addrs} desconectado.")
            self.clientes.pop(name_send)

if __name__ == "__main__":
    servidor = Servidor()
    servidor.init()
    threading.Thread(target=servidor.thread_connect_user).start()
