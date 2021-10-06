import socket 
import threading

'''
HEADER: representa o número de bytes que o recv() vai receber

PORT: é a porta que vai ser reservada no pelo servidor

SERVER: determina o número de IP que o host tem, a função socket.gethostbyname() traduz o nome do host
para o formato de endereço IPV4 e a função socket.gethostname() retorna a máquina onde o interpretador
python está executando atualmente

ADDR: é uma tupla que recebe os valores determinados pelo SERVER e PORT

FORMAT: é a forma que as mensagens vão ser codificadas, ou decodificadas. No caso UTF-8

DISCONNECT_MESSAGE: é o comando padrão que serviria de configuração pro servidor encerrar,
mas não foi utilizado
'''

HEADER = 64
PORT = 12345
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "/sair"

'''
A variavel 'server' recebe através da biblioteca socket, é designado o AF_INET(tipo de endereço IPV4)
SOCK_STREAM é o tipo de socket implementado no procolos TCP/IP, e é esse protocolo q nosso servidor
vai utilizar.

Esse mesmo 'server' vai receber a função setsockopt() pra definir os meios pra controlar o comportamento
do socket.
o SOL_SOCKET ajuda a definir o nível de socket que vamos criar, no caso SO_REUSEADDR, que faz
com que 2 sockets utilizem uma mesma porta de internet. Veio como alternativa pra contornar fechamentos
inesperados do servidor, que mesmo com o religamento do mesmo não recebiam permissão
de acessar a mesma porta por ela já esta vinculada ao socket anterior, e o 1 é o valor da opção escolhida
'''
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind função bind() vincula um nome local único ao soquete com o descritor de soquete, passando
#o endereço adquirido anteriormente
server.bind(ADDR)

# Lista onde vai ser armazenados todos os clientes presentes no servidor
clientes = []

'''
Funções utilizadas em cliente:

encode(): 
    encode(Base64) é o metodo de codificação de bytes para strings
    encode(UTF-8) é o metodo que codifica strings em sequencias de bytes
    Cada método escreve de forma diferente a codificação

decode():
    Retorna o valor original dado pelo encode(), fazendo com que os dados ali sejam decodificados para
    método decode() solicidado. Ex: decode(UTF-8), que a partir dos bytes gerados,
    ele transforma novamente numa string

recv():
    Retorna os bytes recebidos, onde precisa ser determinado o tamanho desses blocos a serem recebidos
    O tamanho declarado deve ser na potencia de 2 para garantir melhor compatibilidade
close():
    Encerra a conexão do socket com o servidor
'''

def cliente(conn, addr):
    #Define a variavel connected do cliente como true, e enquanto True o while vai rodar
    #Envia pro cliente a mensagem requisitando seu apelido
    #Define a variavel first_msg = 0 como indicativo de que a primeira mensagem vai definir o nick
    connected = True
    conn.send('\nDigite seu apelido:\n'.encode(FORMAT))
    first_msg = 0
    while connected:
        '''
        O cliente envia 2 send, o primeiro recv() pega o o valor que representa o tamanho da mensagem
        em bytes, em blocos do tamanho HEADER(64) a partir da decodificação do formato FORMAT (utf-8)
        '''
        len_msg = conn.recv(HEADER).decode(FORMAT)
        len_msg = int(len_msg)
        '''
        Se não for a primeira mensagem, é tratado como uma mensagem a ser enviada pra todos do server
        first_msg1 para não é primeira, 0 para primeira.
        '''
        if first_msg==1:
            #pega o segundo send do cliente e baseado no tamanho declarado pelo primeiro send
            #ele escreve o que decodificar na variável msg
            msg = conn.recv(len_msg).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
                break
            '''
            Constroi o formato da mensagem que vai ser enviado ao servidor e outros clientes
            Para o servidor: [NICKNAME_CLIENTE | IP_CLIENTE:PORTA_CLIENTE]: MENSAGEM_CLIENTE
            Para os clientes: NICKNAME_CLIENTE: MENSAGEM_CLIENTE
            '''
            msg_tosend = '\n'+str(nome)+': '+str(msg)+'\n'
            print(f"[ {nome} | {addr[0]}:{addr[1]}]: {msg}")
            Broadcast(conn, msg_tosend)

        elif first_msg==0:
            '''
            Se for a primeira mensagem, o socket do cliente é adicionado a lista de clientes, depois o
            segundo send é atribuido a variável 'nome', e o valor de first_msg é atualizado
            se o nome for igual a mensagem de desconexão, o nome é alterado para unnamed_user e a variável
            connected é atualizado e o loop é quebrado

            Caso contrario uma mensagem de que o usuário entrou é enviada a todos do chat, e o servidor recebe
            uma confirmação de conexão a partir do nick
            '''
            clientes.append(conn)
            nome = conn.recv(len_msg).decode(FORMAT)
            first_msg = 1
            if nome == DISCONNECT_MESSAGE:
                nome = 'unnamed_user'
                connected = False
                break
            '''
            Se a conexão for feita corretamente, uma mensagem previamente formatada
            é enviada a todos online no chat com o nome do usuário que entrou
            e o servidor também recebe uma atualização.
            '''
            msg_tosend = '\n** '+str(nome)+' acabou de entrar no chat. **\n'
            print(f"[CONEXÃO] {nome} se conectou.")
            Broadcast(conn, msg_tosend)
    # Ao sair do loop, a função desconectar, enviando o socket e o nome
    desconectar(conn, nome)

'''
Função responsável por enviar mensagens a todos do servidor sem incluir proprio usuário que enviou
O try tenta enviar para todos na lista de clientes, mas se algum usuário desconectou de forma indevida 
é chamada a função desconectar pra aquele usuário ser removido da lista
'''
def Broadcast(conn, msg):
    for user in clientes: 
        if user != conn:
            try:
                user.send(msg.encode(FORMAT))
            except:
                desconectar(user)

'''
A função desconectar faz com que o usuário solicitado seja removido da lista de clientes
e o socket de conexão é fechado no servidor. Uma mensagem é enviada tanto pro servidor
quanto pros usuários conectados de que o usuário saiu.
conn.close() fecha a conexão do socket do cliente e conn.remove() retira o cliente da lista de clientes
Por fim, atualiza o número de threads ativas - 2(thread principal e thread do cliente atual)
'''               
def desconectar(conn, nome=None):
    if conn in clientes: 
        print(f"[CONEXÃO] {nome} se desconectou.")
        msg_tosend = '\n** '+str(nome)+' se desconectou do chat. **\n'
        Broadcast(conn, msg_tosend)
        conn.close()
        clientes.remove(conn)
        print("[CONEXÕES ATIVAS] -----> || {} ||".format(threading.activeCount() - 2))

'''
Envia a todos do servidor que o servidor está sendo fechado
Foi pensado em forçar a desconexão dos mesmos inicialmente
'''
def desconn_clientes():
    try:
        for cliente in clientes:
            Broadcast(server,'\nServidor não está aceitando mais conexões, por favor saia.')
            #desconectar(cliente)
    except:
        pass


server_status = True


#Tentativa de criar um comando de shutdown server que desconectasse todos os usuários
'''
def shutdown():
    global server_status
    while(server_status):
        msg = input()
        if msg == DISCONNECT_MESSAGE:
            server_status = False
            desconn_clientes()
'''

def start():
    #a variável server_status iria possuir interaçao com a função shutdown também
    global server_status
    # No modo listen o server vai entrar no modo capaz de aceitar conexões
    server.listen()
    print(f"[LIGADO] Servidor Ligado\n\nIP: {SERVER}\nPort: {PORT}\n")

    #enquanto o servidor estivesse com server_status == True, ele aceita os casos a seguir
    while(server_status):
        try:
            '''
            O server executa a função accept() retorna as duas variáveis e as armazena em conn e addr
            Conn é objeto soquete utilizável para enviar e receber os dados,
            addr é o endereço que está vinculado ao soquete na outro cliente.
            '''

            conn, addr = server.accept()

            '''
            A variável thread especifíca o inicio de uma Thread com a função alvo cliente()
            levando as variáveis conn e addr adquiridas anteriormente logo em seguida 
            pela função start(), as funções são executadas em paralelo com a thread principal.
            '''
            thread = threading.Thread(target=cliente, args=(conn, addr))
            thread.start()
            '''
            Retorna ao servidor que uma conexão foi ativa e retorna o número de conexões existentes
            mas é preciso desconsiderar a thread principal da contagem, logo se diminui 1 do valor
            retornado pelo activeCount()
            '''

            print("[CONEXÕES ATIVAS] -----> || {} ||".format(threading.activeCount() - 1))

        except:
            break
    #Executa a função desconn_clientes() após sair do while(server_status)
    desconn_clientes()
    '''
    A função server.close() marca o socket armazenado pelo server como fechado,
    e todas as operações futuras sobre ele vão falhar
    ''' 
    server.close()
    print("\nServidor em modo de desligamento.")
    
    

#Descreve mensagem de ligar o servidor e executa a função start()
print("Ligando Servidor...")
start()
