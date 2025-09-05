import os
import binascii

class KeyManager:
    def __init__(self, media_id: int, base_dir: str):
        self.media_id = media_id
        self.base_dir = base_dir

    def generate_key_file(self):
        key_path = os.path.join(self.base_dir, f"{self.media_id}.key")
        key_bytes = os.urandom(16)
        with open(key_path, 'wb') as key_file:
            key_file.write(key_bytes)
        return key_path, key_bytes

    def generate_keyinfo_file(self, key_path):
        iv = binascii.hexlify(os.urandom(16)).decode()
        key_uri = f"../{self.media_id}.key"
        keyinfo_path = os.path.join(self.base_dir, f"{self.media_id}.keyinfo")
        with open(keyinfo_path, 'w') as f:
            f.write(f"{key_uri}\n{key_path}\n{iv}\n")
        return keyinfo_path
