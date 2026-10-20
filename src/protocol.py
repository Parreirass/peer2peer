import socket
import struct
import json

def send_message(sock, msg_type, headers, payload=b""):
    headers['type'] = msg_type
    headers['payload_size'] = len(payload)
    
    json_bytes = json.dumps(headers).encode('utf-8')
    header_length_bytes = struct.pack('!I', len(json_bytes))
    
    # Envia tudo de uma vez garantindo a ordem
    sock.sendall(header_length_bytes + json_bytes + payload)

def recvall(sock, n):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None # Conexão fechada
        data.extend(packet)
    return bytes(data)

def receive_message(sock):
    # Lê os 4 bytes iniciais que dizem o tamanho do JSON
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None, None
    
    msglen = struct.unpack('!I', raw_msglen)[0]
    
    # Lê o JSON
    json_bytes = recvall(sock, msglen)
    if not json_bytes:
        return None, None
        
    headers = json.loads(json_bytes.decode('utf-8'))
    
    # Lê o bloco binário (se houver)
    payload_size = headers.get('payload_size', 0)
    payload = b""
    if payload_size > 0:
        payload = recvall(sock, payload_size)
        if payload is None:
            return None, None
            
    return headers, payload