import hashlib
import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: ./py.py [hash]")
        exit(1)
    else:
        hash = sys.argv[1]
        print("Hash: " + hash)
        print("Decrypted: " + hashlib.md5(hash.encode()).hexdigest())

try:
    main()
except KeyboardInterrupt:
    print("\nExiting...")
    exit(1)
