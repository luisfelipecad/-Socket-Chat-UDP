import os
import socket
import threading

hostServidor = '10.113.60.230'
host = '10.113.60.210' 
porta = 12346  # PORTA QUE O CLIENTE VAI OUVIR
portaDestino = 12345 # PORTA QUE O SERVIDOR ESTÁ OUVINDO

contatos = []

# Cria um objeto socket UDP
socket_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Liga o socket ao endereço e porta especificados
socket_server.bind((host, porta))

print(f"Servidor UDP aguardando mensagens em {host}:{porta}")


def limparTela():
    if os.name == 'posix':
        os.system('clear')
    elif os.name == 'nt':
        os.system('cls')


def obterContatoPorCampo(nomeCampo, valorCampo):
    global contatos

    contatoEncontrado = None

    for contato in contatos:
        if (contato[nomeCampo] == valorCampo):
            contatoEncontrado = contato
            break

    return contatoEncontrado


def receber_mensagens():
    global contatos

    while True:
        try:
            # Recebe os dados e o endereço do remetente
            dados, endereco = socket_server.recvfrom(
                1024)  # Tamanho do buffer é 1024 bytes

            mensagem = dados.decode('utf-8')

            if (endereco[0] == hostServidor and endereco[1] == 12345):
                contatos = []

                linhas = mensagem.split("\n")

                for linha in linhas:
                    if (linha):
                        nome, ip = linha.split(",")
                        contatos.append({"nome": nome, "ip": ip})

                limparTela()

                print('\nLista de contatos atualizada!\n')

                for contato in contatos:
                    print(f"IP: {contato['ip']}, Nome: {contato['nome']}")
            else:
                contatoEncontrado = obterContatoPorCampo('ip', endereco[0])

                if (contatoEncontrado is not None):
                    print(f"{contatoEncontrado['nome']} disse: {mensagem}")
                else:
                    print(f"{endereco[0]} disse: {mensagem}")

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

    while True:
        destino_ip = input("\nDigite o endereço IP de destino: ")
        mensagem = input("Digite a mensagem a ser enviada: ")

        if mensagem == "/sair":
            print("Encerrando o programa...")
            print("Fechando portas de escuta:")
            thread_recebimento.join()
            break
        elif mensagem.startswith(".") and not '.contatos' in mensagem and not '.entrar' in mensagem:
            destinatario = obterContatoPorCampo(
                'nome', mensagem.split()[0].replace('.', ''))

            if (destinatario == None):
                print('Contato não encontrado')
            else:
                separator = ' '

                mensagemParaEnviar = separator.join(mensagem.split()[1:])

                cliente_socket.sendto(mensagemParaEnviar.encode(
                    'utf-8'), (destinatario['ip'], portaDestino))
        else:
            cliente_socket.sendto(mensagem.encode(
                'utf-8'), (destino_ip, portaDestino))


# Inicializa uma thread para enviar mensagens
thread_envio = threading.Thread(target=enviar_mensagens)
thread_envio.start()

# Aguarda as threads finalizarem
thread_envio.join()
print("Threads encerradas.")
# Feche o socket (isso nunca será executado no loop acima)
socket_server.close()
print("Socket encerrado. Bye Bye")
