CC = gcc
CFLAGS = -O2 -Wall -Wextra

BINARIES = rc4Encryptor rc4Decryptor

.PHONY: all clean test gui package help

all: $(BINARIES)

rc4Encryptor: rc4_encrypt.c
	$(CC) $(CFLAGS) $< -o $@

rc4Decryptor: rc4_decrypt.c
	$(CC) $(CFLAGS) $< -o $@

test: $(BINARIES)
	@chmod +x verify.sh rc4Encrypt.py rc4Decryptor.py rc4_gui.py
	@./verify.sh

gui:
	@python3 rc4_gui.py

clean:
	rm -f $(BINARIES) rc4Encrypt *.o rc4_assignment.zip

package: clean
	@zip -q rc4_assignment.zip \
		rc4Encrypt.py \
		rc4Decryptor.py \
		rc4_encrypt.c \
		rc4_decrypt.c \
		rc4_gui.py \
		rc4_decrypt_prompt.py \
		file.txt \
		Makefile \
		verify.sh \
		README.md
	@echo "[+] Submission package created: rc4_assignment.zip"

help:
	@echo "RC4 Stream Cipher - Available Targets:"
	@echo "  make          - Compile C binaries (rc4Encryptor, rc4Decryptor)"
	@echo "  make test     - Run the automated 8-part verification test suite"
	@echo "  make gui      - Launch the graphical user interface"
	@echo "  make package  - Create a clean submission archive (rc4_assignment.zip)"
	@echo "  make clean    - Remove compiled binaries and temporary files"
