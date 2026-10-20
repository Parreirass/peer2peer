import os
import math
import hashlib
import threading

class FileManager:
    def __init__(self, filepath, total_size, block_size, is_seeder=False):
        self.filepath = filepath
        self.total_size = total_size
        self.block_size = block_size
        self.total_blocks = math.ceil(total_size / block_size) if total_size > 0 else 0
        self.is_seeder = is_seeder
        
        self.lock = threading.Lock()
        self.available_blocks = set()

        self._initialize_file()

    def _initialize_file(self):
        """Prepara o arquivo no disco (aloca espaço se for leecher)."""
        if self.is_seeder:
            if not os.path.exists(self.filepath):
                raise FileNotFoundError(f"Arquivo Seeder não encontrado: {self.filepath}")
            self.available_blocks = set(range(self.total_blocks))
        else:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            if not os.path.exists(self.filepath):
                with open(self.filepath, 'wb') as f:
                    if self.total_size > 0:
                        f.seek(self.total_size - 1)
                        f.write(b'\0')

    def has_block(self, index):
        with self.lock:
            return index in self.available_blocks

    def is_complete(self):
        with self.lock:
            return len(self.available_blocks) == self.total_blocks

    def get_missing_blocks(self):
        with self.lock:
            return list(set(range(self.total_blocks)) - self.available_blocks)

    def read_block(self, index):
        if not self.has_block(index):
            return None
        with self.lock:
            with open(self.filepath, 'rb') as f:
                f.seek(index * self.block_size)
                bytes_to_read = min(self.block_size, self.total_size - (index * self.block_size))
                return f.read(bytes_to_read)

    def write_block(self, index, data):
        with self.lock:
            if index in self.available_blocks:
                return False
            with open(self.filepath, 'r+b') as f:
                f.seek(index * self.block_size)
                f.write(data)
            self.available_blocks.add(index)
            return True

    def calculate_file_hash(self):
        """Calcula o SHA-256 do arquivo no disco."""
        sha256 = hashlib.sha256()
        with self.lock:
            with open(self.filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256.update(byte_block)
        return sha256.hexdigest()