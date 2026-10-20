import os
import hashlib
import json

def generate_random_file(filepath, size_bytes):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'wb') as f:
        f.write(os.urandom(size_bytes))

def calculate_sha256(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256.update(byte_block)
    return sha256.hexdigest()

def main():
    # arquivo pequeno
    # FILE_SIZE = 10 * 1024  
    # BLOCK_SIZE = 1024   
    # ARCHIVE_NAME = 'arquivo_1MB'    

    # arquivo medio
    FILE_SIZE = 5 * 1024 * 1024
    BLOCK_SIZE = 4096
    ARCHIVE_NAME = 'arquivo_5MB'  

    # arquivo grande   
    # FILE_SIZE = 20 * 1024 * 1024
    # BLOCK_SIZE = 4096 
    # ARCHIVE_NAME = 'arquivo_10MB'  

    ORIGINAL_FILE = '../data/original/'+ ARCHIVE_NAME +'.bin'
    # DOWNLOAD_FILE = '../data/downloads/'+ ARCHIVE_NAME +'_recebido.bin'
    
    print(f"Gerando arquivo de {ARCHIVE_NAME} para o teste de 4 Peers...")
    generate_random_file(ORIGINAL_FILE, FILE_SIZE)
    file_hash = calculate_sha256(ORIGINAL_FILE)
    print(f"SHA-256 do arquivo original: {file_hash}")

    metadata = {
        "file_name": ARCHIVE_NAME + '.bin',
        "total_size": FILE_SIZE,
        "block_size": BLOCK_SIZE,
        "hash_sha256": file_hash
    }

    # Topologia: A <-> B, A <-> C, B <-> D, C <-> D
    
    peer_a = {
        "peer_id": "PeerA", "ip": "127.0.0.1", "port": 5000,
        "is_seeder": True, "file_path": ORIGINAL_FILE, "file_metadata": metadata,
        "neighbors": [
            {"id": "PeerB", "ip": "127.0.0.1", "port": 5001},
            {"id": "PeerC", "ip": "127.0.0.1", "port": 5002}
        ]
    }

    peer_b = {
        "peer_id": "PeerB", "ip": "127.0.0.1", "port": 5001,
        "is_seeder": False, "file_path": '../data/downloads/peer_b_5MB.bin',
        "neighbors": [
            {"id": "PeerA", "ip": "127.0.0.1", "port": 5000},
            {"id": "PeerD", "ip": "127.0.0.1", "port": 5003}
        ]
    }

    peer_c = {
        "peer_id": "PeerC", "ip": "127.0.0.1", "port": 5002,
        "is_seeder": False, "file_path": '../data/downloads/peer_c_5MB.bin',
        "neighbors": [
            {"id": "PeerA", "ip": "127.0.0.1", "port": 5000},
            {"id": "PeerD", "ip": "127.0.0.1", "port": 5003}
        ]
    }

    peer_d = {
        "peer_id": "PeerD", "ip": "127.0.0.1", "port": 5003,
        "is_seeder": False, "file_path": '../data/downloads/peer_d_5MB.bin',
        "neighbors": [
            {"id": "PeerB", "ip": "127.0.0.1", "port": 5001},
            {"id": "PeerC", "ip": "127.0.0.1", "port": 5002}
        ]
    }

    configs = {'peer_a.json': peer_a, 'peer_b.json': peer_b, 'peer_c.json': peer_c, 'peer_d.json': peer_d}
    os.makedirs('../configs', exist_ok=True)
    
    for filename, conf in configs.items():
        with open(f'../configs/{filename}', 'w', encoding='utf-8') as f:
            json.dump(conf, f, indent=4)
            
    print("Arquivos JSON gerados em 'configs/'")

if __name__ == "__main__":
    main()