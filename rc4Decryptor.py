
def ksa(key: bytes) -> list:
    """Key Scheduling Algorithm """
    key_length = len(key)
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % key_length]) % 256
        S[i], S[j] = S[j], S[i]
    return S

def prga(S: list, data: bytes) -> bytes:
    """Pseudo Random Generation Algorithm """
    S = S.copy()
    i = j = 0
    out = bytearray()
    for byte in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        keystream_byte = S[(S[i] + S[j]) % 256]
        out.append(byte ^ keystream_byte)
    return bytes(out)


def decrypt_file(file: str, key: bytes):
    try:
        # Open the encrypted file in binary mode
        with open(file, 'rb') as f:
            ciphertext = f.read()

        # Decrypt the bytes using the same RC4 key
        plaintext = prga(ksa(key), ciphertext)

        # Write the restored plaintext bytes back to the file
        with open(file, 'wb') as f:
            f.write(plaintext)

        print(f"[+] Successfully decrypted {file}")
    except FileNotFoundError:
        print(f"[-] Error: {file} not found.")

if __name__ == "__main__":
    # the same key I use for encryption
    KEY = b"backtohomebutstillmissthesummercamp#INSA#AASTU2018E.C"

    # exact absolute file path 
    decrypt_file("/home/megbaru/file.txt", KEY)
