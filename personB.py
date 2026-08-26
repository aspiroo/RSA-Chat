import socket
import rsa

publicB, privateB = rsa.newkeys(512)

socketB = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socketB.connect(('localhost', 5000))

A_key_data = socketB.recv(1024)
publicA = rsa.PublicKey.load_pkcs1(A_key_data)

socketB.sendall(publicB.save_pkcs1())
print('sent public key to person A')

data = socketB.recv(1024)
print('received encrypted msg:', data)
plaintext = rsa.decrypt(data, privateB)
print('received decrypted msg:', plaintext.decode())

response = input("enter a msg to send to person A: ")
ciphertext = rsa.encrypt(response.encode(), publicA)
socketB.sendall(ciphertext)
print("sent encrypted msg:" , ciphertext)

socketB.close()