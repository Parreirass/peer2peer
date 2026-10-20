import socket
import threading
import time
import logging
import sys
from protocol import send_message, receive_message
from file_manager import FileManager
from config import load_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')

class Peer:
    def __init__(self, config_path):
        self.config = load_config(config_path)
        self.peer_id = self.config['peer_id']
        self.ip = self.config['ip']
        self.port = self.config['port']
        self.neighbors = self.config['neighbors']
        self.is_seeder = self.config.get('is_seeder', False)
        
        self.file_manager = None
        self.file_meta = None
        
        # Lock para impedir solicitações duplicadas do mesmo bloco
        self.blocks_in_flight_lock = threading.Lock()
        self.blocks_in_flight = set()

        if self.is_seeder:
            self.file_meta = self.config['file_metadata']
            self.file_manager = FileManager(
                self.config['file_path'], self.file_meta['total_size'],
                self.file_meta['block_size'], is_seeder=True
            )

    def start(self):
        logging.info(f"[{self.peer_id}] Iniciando. Escutando em {self.ip}:{self.port}")
        
        # Inicia a Thread do Servidor
        threading.Thread(target=self._server_loop, daemon=True).start()

        # Inicia uma Thread de Cliente para cada vizinho configurado
        if not self.is_seeder:
            for neighbor in self.neighbors:
                threading.Thread(target=self._client_loop, args=(neighbor,), daemon=True).start()

        # Monitora a conclusão do arquivo
        try:
            while True:
                if self.file_manager and self.file_manager.is_complete() and not self.is_seeder:
                    logging.info(f"[{self.peer_id}] DOWNLOAD CONCLUÍDO! Verificando integridade...")
                    if self.file_manager.calculate_file_hash() == self.file_meta['hash_sha256']:
                        logging.info(f"[{self.peer_id}] Integridade confirmada! SHA-256 idêntico ao original.")
                    else:
                        logging.error(f"[{self.peer_id}] FALHA na integridade do arquivo.")
                    break
                time.sleep(2)
            
            logging.info(f"[{self.peer_id}] Operação finalizada. Continuarei servindo blocos (Ctrl+C para sair).")
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            logging.info(f"[{self.peer_id}] Encerrando Peer.")

    # --- SERVIDOR ---
    def _server_loop(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.ip, self.port))
        server.listen(5)

        while True:
            try:
                conn, addr = server.accept()
                threading.Thread(target=self._handle_client, args=(conn,), daemon=True).start()
            except Exception as e:
                logging.error(f"[{self.peer_id}] Erro no servidor: {e}")

    def _handle_client(self, conn):
        try:
            headers, payload = receive_message(conn)
            if not headers: return
            
            msg_type = headers.get('type')
            
            if msg_type == 'GET_META':
                if self.file_meta:
                    send_message(conn, 'META_RESPONSE', self.file_meta)
                else:
                    send_message(conn, 'ERROR', {'message': 'Sem metadados'})

            elif msg_type == 'GET_BLOCK_MAP':
                available = list(self.file_manager.available_blocks) if self.file_manager else []
                send_message(conn, 'BLOCK_MAP_RESPONSE', {'available_blocks': available})

            elif msg_type == 'GET_BLOCK':
                idx = headers.get('block_index')
                if self.file_manager and self.file_manager.has_block(idx):
                    send_message(conn, 'BLOCK_RESPONSE', {'block_index': idx}, self.file_manager.read_block(idx))
                else:
                    send_message(conn, 'ERROR', {'message': 'Bloco indisponível'})
        finally:
            conn.close()

    # --- CLIENTE ---
    def _client_loop(self, neighbor):
        n_ip, n_port, n_id = neighbor['ip'], neighbor['port'], neighbor['id']
        
        while True:
            if self.file_manager and self.file_manager.is_complete():
                break

            try:
                # 1. Pega metadados
                if not self.file_meta:
                    resp, _ = self._request(n_ip, n_port, 'GET_META', {})
                    if resp and resp.get('type') == 'META_RESPONSE':
                        self.file_meta = resp
                        self.file_manager = FileManager(
                            self.config['file_path'], self.file_meta['total_size'], self.file_meta['block_size'], False
                        )
                        logging.info(f"[{self.peer_id}] Metadados recebidos de {n_id}.")
                    else:
                        time.sleep(2)
                        continue

                # 2. Pega mapa de blocos do vizinho
                resp, _ = self._request(n_ip, n_port, 'GET_BLOCK_MAP', {})
                if not resp or resp.get('type') != 'BLOCK_MAP_RESPONSE':
                    time.sleep(2)
                    continue
                
                neighbor_blocks = set(resp.get('available_blocks', []))
                useful_blocks = list(set(self.file_manager.get_missing_blocks()).intersection(neighbor_blocks))
                
                if not useful_blocks:
                    time.sleep(1)
                    continue
                
                # 3. Escolhe um bloco que não está sendo baixado no momento
                target_block = None
                with self.blocks_in_flight_lock:
                    for b in useful_blocks:
                        if b not in self.blocks_in_flight:
                            target_block = b
                            self.blocks_in_flight.add(b)
                            break
                
                if target_block is None:
                    time.sleep(0.5)
                    continue

                # 4. Baixa o bloco
                resp, payload = self._request(n_ip, n_port, 'GET_BLOCK', {'block_index': target_block})
                
                if resp and resp.get('type') == 'BLOCK_RESPONSE':
                    self.file_manager.write_block(target_block, payload)
                    with self.file_manager.lock:
                        percent = (len(self.file_manager.available_blocks) / self.file_manager.total_blocks) * 100
                    logging.info(f"[{self.peer_id}] Bloco {target_block} baixado de {n_id}. Progresso: {percent:.1f}%")
                
                # Libera o bloco para tentar de novo em caso de erro
                with self.blocks_in_flight_lock:
                    self.blocks_in_flight.discard(target_block)

            except ConnectionRefusedError:
                time.sleep(2) # Vizinho offline
            except Exception as e:
                time.sleep(2)

    def _request(self, ip, port, msg_type, headers):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5.0)
            sock.connect((ip, port))
            send_message(sock, msg_type, headers)
            return receive_message(sock)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python peer.py <caminho_do_config.json>")
        sys.exit(1)
    Peer(sys.argv[1]).start()