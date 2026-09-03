import socket
import threading
import rsa

publicA, privateA = rsa.newkeys(512)
socketA = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socketA.bind(('localhost', 5000))

socketA.listen(1)
print("waiting for msg...")

connected_socket, address = socketA.accept()
print('connected to:', address)

connected_socket.sendall(publicA.save_pkcs1())
print('sent public key to person B')

B_key_data = connected_socket.recv(1024)
publicB = rsa.PublicKey.load_pkcs1(B_key_data)
print('received public key from person B, ready to chat (type "exit" to quit)')

running = True
cipher_len = (publicA.n.bit_length() + 7) // 8


def recv_exact(n):
    buf = b''
    while len(buf) < n:
        chunk = connected_socket.recv(n - len(buf))
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
        plaintext = rsa.decrypt(data, privateA)
        print('\nB:', plaintext.decode())
        if plaintext.decode() == 'exit':
            running = False
            break


def send_loop():
    global running
    while running:
        try:
            message = input('A: ')
        except EOFError:
            message = 'exit'
        ciphertext = rsa.encrypt(message.encode(), publicB)
        try:
            connected_socket.sendall(ciphertext)
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

connected_socket.close()
socketA.close()
