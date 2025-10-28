import os, uuid, argparse
from app.crypto_engine import encrypt_file, decrypt_file

def main():
    parser = argparse.ArgumentParser(description="Obscuron CLI Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Encrypt
    enc_parser = subparsers.add_parser("encrypt", help="Encrypt a file")
    enc_parser.add_argument("-i", "--input", required=True, help="Input file path")
    enc_parser.add_argument("-p", "--password", required=True, help="Encryption password")
    enc_parser.add_argument("-o", "--output", help="Output file path (.obsx)")

    # Decrypt
    dec_parser = subparsers.add_parser("decrypt", help="Decrypt a file")
    dec_parser.add_argument("-i", "--input", required=True, help="Input .obsx file path")
    dec_parser.add_argument("-p", "--password", required=True, help="Decryption password")
    dec_parser.add_argument("-o", "--output", help="Output file path (restored original)")

    args = parser.parse_args()

    if args.command == "encrypt":
        with open(args.input, "rb") as f:
            data = f.read()
        enc_bytes = encrypt_file(data, args.password, os.path.basename(args.input))
        out_path = args.output or f"{uuid.uuid4().hex}.obsx"
        with open(out_path, "wb") as f:
            f.write(enc_bytes)
        print(f"Encrypted: {out_path}")

    elif args.command == "decrypt":
        with open(args.input, "rb") as f:
            enc_bytes = f.read()
        plain, orig_name, ext = decrypt_file(enc_bytes, args.password)
        out_path = args.output or orig_name
        with open(out_path, "wb") as f:
            f.write(plain)
        print(f"Decrypted: {out_path}")

if __name__ == "__main__":
    main()
