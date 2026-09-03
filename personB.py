import socket
import threading
import rsa

publicB, privateB = rsa.newkeys(512)

socketB = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socketB.connect(('localhost', 5000))

A_key_data = socketB.recv(1024)
publicA = rsa.PublicKey.load_pkcs1(A_key_data)

socketB.sendall(publicB.save_pkcs1())
print('sent public key to person A')
print('ready to chat (type "exit" to quit)')

running = True
cipher_len = (publicB.n.bit_length() + 7) // 8


def recv_exact(n):
    buf = b''
    while len(buf) < n:
        chunk = socketB.recv(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf


def receive_loop():
    global running
    while running:
        try:
            data = recv_exact(cipher_len)
        except OSError:
            break
        if not data:
            break
        plaintext = rsa.decrypt(data, privateB)
        print('\nA:', plaintext.decode())
        if plaintext.decode() == 'exit':
            running = False
            break


def send_loop():
    global running
    while running:
        try:
            message = input('B: ')
        except EOFError:
            message = 'exit'
        ciphertext = rsa.encrypt(message.encode(), publicA)
        try:
            socketB.sendall(ciphertext)
        except OSError:
            break
        if message == 'exit':
            running = False
            break


receiver = threading.Thread(target=receive_loop, daemon=True)
sender = threading.Thread(target=send_loop, daemon=True)

receiver.start()
sender.start()

sender.join()
receiver.join(timeout=1)

socketB.close()
