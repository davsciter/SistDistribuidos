import socket
import threading

'''
HEADER: representa o número de bytes que o recv()/send() vai receber

PORT: é a porta que vai ser utilizada para conectar ao servidor

SERVER: determina o número de IP que o host tem, a função socket.gethostbyname() traduz o nome do host
para o formato de endereço IPV4 e a função socket.gethostname() retorna a máquina onde o interpretador
python está executando atualmente. Como estamos utilizando tanto cliente quanto servidor na mesma
maquina a representação desde modo não afetaria, mas é importante que o endereço de IP armazenado ali
seja o IP do servidor que vai ser conectado.

ADDR: é uma tupla que recebe os valores determinados pelo SERVER e PORT

FORMAT: é a forma que as mensagens vão ser codificadas, ou decodificadas. No caso UTF-8

DISCONNECT_MESSAGE: é o comando padrão que ao usuário enviar, faz com que ele fecha a conexão dele com
o servidor e realize a funções de desconexão
'''

HEADER = 64
PORT = 12345
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "/sair"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)


'''
A variavel 'client' recebe através da biblioteca socket, é designado o AF_INET(tipo de endereço IPV4)
SOCK_STREAM é o tipo de socket implementado no procolos TCP/IP, e é esse protocolo que o cliente
vai utilizar.

A partir desse 'client' gerado, ele vai ser 'connect' ao endereço armazenado anteriormente, enquanto
o servidor estiver em modo listen()
'''
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

#Variável global que determina a situação do cliente, como conectado = True
conectado = True

#Função que vai tratar a mensagem antes de enviar, dependendo se for o tamanho da string ou a própria string

def msg_tratada(msg, tratar_length=True):
    if tratar_length:
        #Codifica a mensagem no FORMAT declarado e atribui a variável 'message'
        message = msg.encode(FORMAT)
        #Reserva o tamanho da mensagem codificado
        msg_length = len(message)
        #Prepara pra enviar o tamanho da mensagem codificada no valor de string ao servidor, pelo FORMAT
        send_length = str(msg_length).encode(FORMAT)
        #Soma o tamanho da mensagem codificada, ao número de b' '(bytes) vezes
        #o (HEADER-tamanho da mensagem codificada)
        send_length += b' ' * (HEADER - len(send_length))
        #Define o valor que vai ser retornado pela função
        msg_tratada = send_length
    else:
        #simplesmente codifica a string do input no formato FORMAT
        msg_tratada = msg.encode(FORMAT)
    #retorna a quem solicitou a msg_tratada
    return msg_tratada

'''
A função sendo() roda em threading pelo cliente, acessando a variável global conectado
E enquanto estiver conectado ele aceita input como mensagem()
'''
def send():
    try:
        global conectado
        while conectado:
            msg = input()
            #Se a mensagem bater com o DISCONNECT_MESSAGE, a variável conectado muda para falso 
            #e a mensagem é tratada uma última vez para enviar ao servidor que o cliente saiu
            #Caso seja uma mensagem normal, ele só envia o tamanho da mensagem pelo primeiro send, e
            #no segundo send ele envia a string da mensagem
            if msg == DISCONNECT_MESSAGE:
                conectado = False
            client.send(msg_tratada(msg))
            client.send(msg_tratada(msg, False))
    except:
        pass


#Inicia a thread snd (send), que executa a função send em paralelo e por depois inicia ela pelo start()
snd = threading.Thread(target=send, args=())
snd.start()

#A thread principal, enquanto a variavel conectada for True, vai receber mensagens e printar pro cliente
#O recv vai aceitar blocos decodificados no FORMAT desejado de até 2048 bytes.
while conectado:
    msg = client.recv(2048).decode(FORMAT)
    print(msg)
    