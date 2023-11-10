import socket
import threading

host = '10.113.60.230'
porta = 12345  # PORTA QUE O SERVIDOR VAI OUVIR
portaCliente = 12346  # PORTA QUE O CLIENTE VAI OUVIR

# Cria um objeto socket UDP
socket_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Liga o socket ao endereço e porta especificados
socket_server.bind((host, porta))

# Tamanho máximo de dados a serem recebidos de uma vez
tamanho_maximo = 1024

# Lista para armazenar pares de nome e IP
participantes = []

# Variável para controlar a execução do programa
executando = True

print(f"Servidor UDP aguardando mensagens em {host}:{porta}")

# Função para remover um participante da lista pelo nome


def remover_participante(nome):
    for participante in participantes:
        if participante[0] == nome:
            participantes.remove(participante)
            print(f"{nome} saiu da sala")

# Função para responder aos contatos com a lista de participantes


def responder_contatos(endereco):
    lista_contatos = ""
    for nome, ip in participantes:
        lista_contatos = lista_contatos+(f"{nome},{ip}\n")
    # print(lista_contatos)
    # Divide a lista em pedaços para enviar
    pedacos = [lista_contatos[i:i + tamanho_maximo]
               for i in range(0, len(lista_contatos), tamanho_maximo)]
    # Envia cada pedaço
    for pedaco in pedacos:
        socket_server.sendto(pedaco.encode('utf-8'),
                             (endereco[0], portaCliente))

# Função para receber mensagens


def receber_mensagens():
    while executando:
        try:
            # Recebe os dados e o endereço do remetente
            dados, endereco = socket_server.recvfrom(
                tamanho_maximo)  # Tamanho do buffer é 1024 bytes

            mensagem = dados.decode('utf-8')
            if mensagem.startswith(".entrar "):
                nome = mensagem[8:]  # Extrai o nome da mensagem
                # Adiciona o par (nome, IP) à lista
                participantes.append((nome, endereco[0]))
                print(nome+" adicionado na lista.")
                lista_contatos = "\n".join(
                    [f"{nome},{ip}" for nome, ip in participantes])
                print(lista_contatos)
            elif mensagem.startswith(".sair "):
                nome = mensagem[6:]  # Extrai o nome da mensagem
                remover_participante(nome)
            elif mensagem == ".contatos":
                responder_contatos(endereco)
            print(f"Recebido de {endereco[0]}:{endereco[1]}: {mensagem}")

        except UnicodeDecodeError:
            print(
                f"Recebido de {endereco[0]}:{endereco[1]}: Erro de decodificação (não UTF-8)")


# Inicializa uma thread para receber mensagens
thread_recebimento = threading.Thread(target=receber_mensagens)
thread_recebimento.daemon = True
thread_recebimento.start()

# Função para enviar mensagens


def enviar_mensagens():
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    global executando
    destino_ip = input("Digite o endereço IP de destino: ")
    if destino_ip == "":
        destino_ip = host
    while executando:
        mensagem = input("\n"+"Digite a mensagem a ser enviada: ")
        if mensagem == ".parar":
            print("Encerrando o programa...")
            print("Fechando portas de escuta:")
            executando = False
            cliente_socket.sendto(mensagem.encode(
                'utf-8'), (host, portaCliente))
        elif mensagem.startswith(".destino"):
            destino_ip = input("Digite o endereço IP de destino: ")
        else:
            cliente_socket.sendto(mensagem.encode(
                'utf-8'), (destino_ip, portaCliente))


# Inicializa uma thread para enviar mensagens
thread_envio = threading.Thread(target=enviar_mensagens)
thread_envio.start()

# Aguarda as threads finalizarem
thread_recebimento.join()
thread_envio.join()

print("Threads encerradas.")
# Feche o socket (isso nunca será executado no loop acima)
socket_server.close()
print("Socket encerrado. Bye Bye")
