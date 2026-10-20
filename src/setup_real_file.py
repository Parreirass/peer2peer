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
    DOWNLOAD_FILE = f'../data/downloads/recebido_{NOME_DO_ARQUIVO}'
    BLOCK_SIZE = 4096 # 4 KB
    
    if not os.path.exists(ORIGINAL_FILE):
        print(f"ERRO: Não encontrei o arquivo '{ORIGINAL_FILE}'.")
        print("Certifique-se de colar o arquivo real na pasta 'data/original/'.")
        return

    # Extrai o tamanho real e o Hash do seu arquivo
    FILE_SIZE = os.path.getsize(ORIGINAL_FILE)
    file_hash = calculate_sha256(ORIGINAL_FILE)
    
    print(f"Analisando arquivo real: {NOME_DO_ARQUIVO}")
    print(f"Tamanho: {FILE_SIZE} bytes")
    print(f"SHA-256: {file_hash}")

    # Cria os Metadados
    metadata = {
        "file_name": NOME_DO_ARQUIVO,
        "total_size": FILE_SIZE,
        "block_size": BLOCK_SIZE,
        "hash_sha256": file_hash
    }

    # Configura o Seeder (Peer A) e Leecher (Peer B)
    peer_a_config = {
        "peer_id": "PeerA", "ip": "127.0.0.1", "port": 5000,
        "is_seeder": True, "file_path": ORIGINAL_FILE,
        "file_metadata": metadata, "neighbors": []
    }

    peer_b_config = {
        "peer_id": "PeerB", "ip": "127.0.0.1", "port": 5001,
        "is_seeder": False, "file_path": DOWNLOAD_FILE,
        "neighbors": [{"id": "PeerA", "ip": "127.0.0.1", "port": 5000}]
    }

    # Salva os arquivos JSON
    os.makedirs('../configs', exist_ok=True)
    with open('../configs/peer_a.json', 'w', encoding='utf-8') as f:
        json.dump(peer_a_config, f, indent=4)
    with open('../configs/peer_b.json', 'w', encoding='utf-8') as f:
        json.dump(peer_b_config, f, indent=4)
        
    print("\nConfigs atualizadas! Pode rodar os Peers.")

if __name__ == "__main__":
    main()