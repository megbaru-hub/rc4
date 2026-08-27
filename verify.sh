#!/bin/bash
# ==============================================================================
# RC4 Implementation Automated Verification Test Suite
# ==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PASSED_TESTS=0
TOTAL_TESTS=0
TEST_DIR=$(mktemp -d -t rc4_test_XXXXXX)

cleanup() {
    rm -rf "$TEST_DIR"
}
trap cleanup EXIT

print_header() {
    echo -e "${BLUE}${BOLD}======================================================================${NC}"
    echo -e "${BLUE}${BOLD}                  RC4 CIPHER VERIFICATION SUITE                       ${NC}"
    echo -e "${BLUE}${BOLD}======================================================================${NC}"
    echo ""
}

run_test() {
    local test_name="$1"
    local command="$2"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "${BOLD}[Test $TOTAL_TESTS] $test_name...${NC}"
    
    if eval "$command"; then
        echo -e "  ${GREEN}✓ PASSED${NC}\n"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "  ${RED}✗ FAILED${NC}\n"
    fi
}

print_header

# Test 1: Compile Native C Binaries
run_test "Compiling native C implementation using GCC" '
    gcc -O2 "$SCRIPT_DIR/rc4_encrypt.c" -o "$TEST_DIR/rc4Encryptor_c" && \
    gcc -O2 "$SCRIPT_DIR/rc4_decrypt.c" -o "$TEST_DIR/rc4Decryptor_c"
'

# Test 2: Python Script Executability & Shebang
run_test "Verifying Python scripts executable permissions and shebang" '
    [ -x "$SCRIPT_DIR/rc4Encrypt.py" ] && [ -x "$SCRIPT_DIR/rc4Decryptor.py" ] && \
    head -n 1 "$SCRIPT_DIR/rc4Encrypt.py" | grep -q "^#!/usr/bin/env python3"
'

# Test 3: Basic Python Encrypt/Decrypt Roundtrip Integrity
run_test "Python Encryption & Decryption Data Integrity (XOR symmetry)" '
    echo "RC4 verification sample plaintext payload 123456!" > "$TEST_DIR/sample1.txt"
    ORIG_HASH=$(sha256sum "$TEST_DIR/sample1.txt" | awk "{print \$1}")
    
    # Encrypt
    PYTHONPATH="$SCRIPT_DIR" python3 -c "import rc4Encrypt; rc4Encrypt.encrypt_file(\"$TEST_DIR/sample1.txt\", b\"secret-eval-key-2026\")" >/dev/null
    ENC_HASH=$(sha256sum "$TEST_DIR/sample1.txt" | awk "{print \$1}")
    
    # Assert ciphertext != plaintext
    [ "$ORIG_HASH" != "$ENC_HASH" ] || exit 1
    
    # Decrypt
    PYTHONPATH="$SCRIPT_DIR" python3 -c "import rc4Decryptor; rc4Decryptor.decrypt_file(\"$TEST_DIR/sample1.txt\", b\"secret-eval-key-2026\")" >/dev/null
    DEC_HASH=$(sha256sum "$TEST_DIR/sample1.txt" | awk "{print \$1}")
    
    # Assert restored == original
    [ "$ORIG_HASH" = "$DEC_HASH" ]
'

# Test 4: Native C Binary Encrypt/Decrypt Roundtrip Integrity
run_test "Native C Binary Encryption & Decryption Roundtrip" '
    echo "System-level native C binary testing with buffer safety verification." > "$TEST_DIR/sample2.txt"
    ORIG_HASH=$(sha256sum "$TEST_DIR/sample2.txt" | awk "{print \$1}")
    
    # Encrypt with C binary
    "$TEST_DIR/rc4Encryptor_c" "$TEST_DIR/sample2.txt" "academicKey456" >/dev/null
    ENC_HASH=$(sha256sum "$TEST_DIR/sample2.txt" | awk "{print \$1}")
    [ "$ORIG_HASH" != "$ENC_HASH" ] || exit 1
    
    # Decrypt with C binary
    "$TEST_DIR/rc4Decryptor_c" "$TEST_DIR/sample2.txt" "academicKey456" >/dev/null
    DEC_HASH=$(sha256sum "$TEST_DIR/sample2.txt" | awk "{print \$1}")
    [ "$ORIG_HASH" = "$DEC_HASH" ]
'

# Test 5: Cross-Language Interoperability (Python Encrypt -> C Decrypt)
run_test "Cross-Compatibility: Encrypt with Python -> Decrypt with C Binary" '
    echo "Testing cross-compatibility between Python and C implementations." > "$TEST_DIR/cross1.txt"
    ORIG_HASH=$(sha256sum "$TEST_DIR/cross1.txt" | awk "{print \$1}")
    
    # Encrypt with Python
    PYTHONPATH="$SCRIPT_DIR" python3 -c "import rc4Encrypt; rc4Encrypt.encrypt_file(\"$TEST_DIR/cross1.txt\", b\"UniversalKey#2026\")" >/dev/null
    
    # Decrypt with C binary
    "$TEST_DIR/rc4Decryptor_c" "$TEST_DIR/cross1.txt" "UniversalKey#2026" >/dev/null
    DEC_HASH=$(sha256sum "$TEST_DIR/cross1.txt" | awk "{print \$1}")
    [ "$ORIG_HASH" = "$DEC_HASH" ]
'

# Test 6: Cross-Language Interoperability (C Encrypt -> Python Decrypt)
run_test "Cross-Compatibility: Encrypt with C Binary -> Decrypt with Python" '
    echo "Testing reverse cross-compatibility: C to Python." > "$TEST_DIR/cross2.txt"
    ORIG_HASH=$(sha256sum "$TEST_DIR/cross2.txt" | awk "{print \$1}")
    
    # Encrypt with C binary
    "$TEST_DIR/rc4Encryptor_c" "$TEST_DIR/cross2.txt" "UniversalKey#2026" >/dev/null
    
    # Decrypt with Python
    PYTHONPATH="$SCRIPT_DIR" python3 -c "import rc4Decryptor; rc4Decryptor.decrypt_file(\"$TEST_DIR/cross2.txt\", b\"UniversalKey#2026\")" >/dev/null
    DEC_HASH=$(sha256sum "$TEST_DIR/cross2.txt" | awk "{print \$1}")
    [ "$ORIG_HASH" = "$DEC_HASH" ]
'

# Test 7: Binary / Non-ASCII Payload Handling
run_test "Binary Data Handling (random 16KB binary stream)" '
    head -c 16384 /dev/urandom > "$TEST_DIR/binary_data.bin"
    ORIG_HASH=$(sha256sum "$TEST_DIR/binary_data.bin" | awk "{print \$1}")
    
    "$TEST_DIR/rc4Encryptor_c" "$TEST_DIR/binary_data.bin" "binarySecretKey" >/dev/null
    ENC_HASH=$(sha256sum "$TEST_DIR/binary_data.bin" | awk "{print \$1}")
    [ "$ORIG_HASH" != "$ENC_HASH" ] || exit 1
    
    "$TEST_DIR/rc4Decryptor_c" "$TEST_DIR/binary_data.bin" "binarySecretKey" >/dev/null
    DEC_HASH=$(sha256sum "$TEST_DIR/binary_data.bin" | awk "{print \$1}")
    [ "$ORIG_HASH" = "$DEC_HASH" ]
'

# Test 8: Wrong Key Decryption Fails Integrity (Security property)
run_test "Key Specificity Check (Decryption with wrong key yields scrambled data)" '
    echo "Confidential test payload for key-specificity verification." > "$TEST_DIR/keytest.txt"
    ORIG_HASH=$(sha256sum "$TEST_DIR/keytest.txt" | awk "{print \$1}")
    
    "$TEST_DIR/rc4Encryptor_c" "$TEST_DIR/keytest.txt" "CorrectKey" >/dev/null
    "$TEST_DIR/rc4Decryptor_c" "$TEST_DIR/keytest.txt" "WrongKey" >/dev/null
    DEC_HASH=$(sha256sum "$TEST_DIR/keytest.txt" | awk "{print \$1}")
    
    # Must NOT match original if wrong key used
    [ "$ORIG_HASH" != "$DEC_HASH" ]
'

echo -e "${BLUE}${BOLD}======================================================================${NC}"
if [ "$PASSED_TESTS" -eq "$TOTAL_TESTS" ]; then
    echo -e "${GREEN}${BOLD} ALL $TOTAL_TESTS TESTS PASSED SUCCESSFULLY! (Score: 100%)${NC}"
else
    echo -e "${RED}${BOLD} TEST SUITE FINISHED: $PASSED_TESTS/$TOTAL_TESTS tests passed.${NC}"
fi
echo -e "${BLUE}${BOLD}======================================================================${NC}"
