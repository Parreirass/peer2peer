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
    DOWNLOAD_FILE = '../data/downloads/'+ ARCHIVE_NAME +'_recebido.bin'

    print("Gerando arquivo de teste...")
    generate_random_file(ORIGINAL_FILE, FILE_SIZE)
    file_hash = calculate_sha256(ORIGINAL_FILE)
    print(f"SHA-256: {file_hash}")

    metadata = {
        "file_name": ARCHIVE_NAME + '.bin',
        "total_size": FILE_SIZE,
        "block_size": BLOCK_SIZE,
        "hash_sha256": file_hash
    }

    # Config Peer A (Seeder)
    peer_a_config = {
        "peer_id": "PeerA", "ip": "127.0.0.1", "port": 5000,
        "is_seeder": True, "file_path": ORIGINAL_FILE,
        "file_metadata": metadata, "neighbors": []
    }

    # Config Peer B (Leecher)
    peer_b_config = {
        "peer_id": "PeerB", "ip": "127.0.0.1", "port": 5001,
        "is_seeder": False, "file_path": DOWNLOAD_FILE,
        "neighbors": [{"id": "PeerA", "ip": "127.0.0.1", "port": 5000}]
    }

    os.makedirs('../configs', exist_ok=True)
    with open('../configs/peer_a.json', 'w', encoding='utf-8') as f:
        json.dump(peer_a_config, f, indent=4)
    with open('../configs/peer_b.json', 'w', encoding='utf-8') as f:
        json.dump(peer_b_config, f, indent=4)
        
    print("Configs criadas em 'configs/'")

if __name__ == "__main__":
    main()