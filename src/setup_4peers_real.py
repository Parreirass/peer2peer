import os
import hashlib
import json

def calculate_sha256(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256.update(byte_block)
    return sha256.hexdigest()

def main():
    NOME_DO_ARQUIVO = 'galo.jpg'
    
    ORIGINAL_FILE = f'../data/original/{NOME_DO_ARQUIVO}'
    
    if not os.path.exists(ORIGINAL_FILE):
        print(f"ERRO: Não encontrei '{ORIGINAL_FILE}'.")
        return

    FILE_SIZE = os.path.getsize(ORIGINAL_FILE)
    file_hash = calculate_sha256(ORIGINAL_FILE)
    
    print(f"Preparando 4 Peers para o arquivo: {NOME_DO_ARQUIVO} ({FILE_SIZE} bytes)")

    metadata = {
        "file_name": NOME_DO_ARQUIVO,
        "total_size": FILE_SIZE,
        "block_size": 4096,
        "hash_sha256": file_hash
    }

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
        "is_seeder": False, "file_path": f'../data/downloads/PeerB_recebido_{NOME_DO_ARQUIVO}',
        "neighbors": [
            {"id": "PeerA", "ip": "127.0.0.1", "port": 5000},
            {"id": "PeerD", "ip": "127.0.0.1", "port": 5003}
        ]
    }

    peer_c = {
        "peer_id": "PeerC", "ip": "127.0.0.1", "port": 5002,
        "is_seeder": False, "file_path": f'../data/downloads/PeerC_recebido_{NOME_DO_ARQUIVO}',
        "neighbors": [
            {"id": "PeerA", "ip": "127.0.0.1", "port": 5000},
            {"id": "PeerD", "ip": "127.0.0.1", "port": 5003}
        ]
    }

    peer_d = {
        "peer_id": "PeerD", "ip": "127.0.0.1", "port": 5003,
        "is_seeder": False, "file_path": f'../data/downloads/PeerD_recebido_{NOME_DO_ARQUIVO}',
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
            
    print("Sucesso! peer_c.json e peer_d.json foram criados na pasta 'configs/'.")

if __name__ == "__main__":
    main()