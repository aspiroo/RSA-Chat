# RSA Chat Demo

A small project demonstrating full-duplex, RSA-encrypted chat between two
peers — first as a pair of Python terminal scripts talking over a raw TCP
socket, then as a live two-tab browser demo using the Web Crypto API.

In both versions, each side generates its own RSA keypair, the two sides
exchange public keys, and every message is encrypted with the *recipient's*
public key and decrypted with the *recipient's* private key. Private keys
never leave the machine (or browser tab) that generated them.

"Full-duplex" means either side can send and receive at any time over the
same connection — there's no turn-taking, unlike a simple request/reply
exchange.

## 1. Terminal chat (`personA.py` / `personB.py`)

Two Python scripts that connect over a local TCP socket (`localhost:5000`)
using the [`rsa`](https://pypi.org/project/rsa/) library (512-bit keys, for
demo speed — not production strength). Each script runs a receiver thread
and a sender thread so you can type and read messages concurrently.

### Run it

In one terminal (starts the listener):

```
python personA.py
```

In a second terminal (connects to it):

```
python personB.py
```

Type messages and press Enter to send. Type `exit` on either side to close
the connection.

### How it works

1. `personA.py` binds and listens on `localhost:5000`; `personB.py` connects to it.
2. Each side generates an RSA keypair and sends its **public** key to the other over the socket.
3. A background thread on each side loops on `recv`, decrypting incoming ciphertext with its own private key and printing it.
4. A second loop reads input from the terminal, encrypts it with the *peer's* public key, and sends it.
5. Messages are read in fixed-size chunks matching the RSA key's ciphertext length, so multiple messages sent back-to-back can't get merged into one read and corrupt decryption.

## 2. Browser demo (`webdemo/`)

A live, two-tab chat demo. A small Flask-SocketIO server relays traffic
between exactly two connected browsers; it only ever sees ciphertext — all
RSA-OAEP (2048-bit) key generation, encryption, and decryption happens
client-side via the browser's native Web Crypto API.

### Setup

```
cd webdemo
pip install -r requirements.txt
python server.py
```

### Run it

Open `http://localhost:5001` in two separate browser tabs (or two devices
on the same network, using your machine's LAN address). The first tab to
connect becomes **Person A**, the second becomes **Person B**. Once both
sides show "Encrypted channel ready", type in either tab — messages appear
instantly on the other side, decrypted in-browser.

### How it works

1. On connecting, each tab generates its own RSA-OAEP keypair locally and sends its public key to the server.
2. The server relays public keys and ciphertext between the two connected sockets, caching each peer's public key so a key sent before the other side had joined isn't lost — it's handed over as soon as the second peer connects.
3. Sending a message encrypts it in-browser with the *recipient's* public key before it's transmitted; the recipient decrypts it with its own private key on arrival.
4. Because both directions are driven by independent socket events rather than a request/reply cycle, either tab can send at any time — full duplex.

The dev server (`server.py`) is for local demo use only — not production
hardened.
