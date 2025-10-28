import os, base64, json
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = b"OBSCURON"
VERSION = b"\x01"  # version 1

def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
    )
    return kdf.derive(password.encode())

def encrypt_file(file_bytes: bytes, password: str, filename: str) -> bytes:
    salt = os.urandom(16)
    nonce = os.urandom(12)
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)

    # encrypt metadata+file
    payload = {
        "filename": os.path.basename(filename),
        "ext": os.path.splitext(filename)[1],
        "filedata": base64.b64encode(file_bytes).decode()
    }
    payload_bytes = json.dumps(payload).encode()

    ciphertext = aesgcm.encrypt(nonce, payload_bytes, None)

    # compile .obsx binary file
    return MAGIC + VERSION + salt + nonce + ciphertext

def decrypt_file(enc_bytes: bytes, password: str) -> tuple:
    if not enc_bytes.startswith(MAGIC):
        raise ValueError("Not a valid .obsx file")

    version = enc_bytes[len(MAGIC):len(MAGIC)+1]
    if version != VERSION:
        raise ValueError("Unsupported file version")

    salt = enc_bytes[9:25]    # 16 bytes
    nonce = enc_bytes[25:37]  # 12 bytes
    ciphertext = enc_bytes[37:]

    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    payload_bytes = aesgcm.decrypt(nonce, ciphertext, None)
    payload = json.loads(payload_bytes.decode())

    filedata = base64.b64decode(payload["filedata"])
    filename = payload["filename"]
    ext = payload["ext"]

    return filedata, filename, ext
