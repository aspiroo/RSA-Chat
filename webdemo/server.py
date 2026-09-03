"""
Full-duplex RSA-encrypted chat demo server.

Relays public keys and ciphertext between exactly two browser peers.
The server never sees plaintext or private keys - all RSA-OAEP
encryption/decryption happens client-side via the Web Crypto API.
Run this, then open http://localhost:5001 in two separate browser
tabs (or two devices on the same network) to chat.
"""
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, disconnect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rsa-demo-not-for-production'
socketio = SocketIO(app, async_mode='threading')

# sid -> role ("A" or "B")
peers = {}
# sid -> last public key JWK sent by that peer
public_keys = {}


def other_sid(sid):
    for s in peers:
        if s != sid:
            return s
    return None


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def on_connect():
    if len(peers) >= 2:
        emit('room_full')
        disconnect()
        return
    role = 'A' if 'A' not in peers.values() else 'B'
    from flask import request
    peers[request.sid] = role
    emit('assigned_role', {'role': role})
    peer = other_sid(request.sid)
    if peer:
        emit('peer_joined', room=peer)
        emit('peer_joined')
        # peer may have sent its public key before we connected (nobody was
        # around to relay it then) - hand over the cached copy now.
        if peer in public_keys:
            emit('public_key', {'jwk': public_keys[peer]})


@socketio.on('disconnect')
def on_disconnect():
    from flask import request
    peers.pop(request.sid, None)
    public_keys.pop(request.sid, None)
    peer = other_sid(request.sid)
    if peer:
        emit('peer_left', room=peer)


@socketio.on('public_key')
def on_public_key(data):
    from flask import request
    public_keys[request.sid] = data.get('jwk')
    peer = other_sid(request.sid)
    if peer:
        emit('public_key', data, room=peer)


@socketio.on('cipher_message')
def on_cipher_message(data):
    from flask import request
    peer = other_sid(request.sid)
    if peer:
        emit('cipher_message', data, room=peer)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, use_reloader=False)
