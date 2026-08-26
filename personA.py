import socket
import rsa

publicA,privateA = rsa.newkeys(512)
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

message = input("enter a msg to send to person B: ")
ciphertext = rsa.encrypt(message.encode(), publicB)
connected_socket.sendall(ciphertext)
print("sent encrypted msg:" , ciphertext)

data = connected_socket.recv(1024)
print('received encrypted msg:', data)
plaintext = rsa.decrypt(data, privateA)
print('received decrypted msg: ', plaintext.decode())

connected_socket.close()
socketA.close()