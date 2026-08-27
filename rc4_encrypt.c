#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define DEFAULT_KEY "backtohomebutstillmissthesummercamp#INSA#AASTU2018E.C"
#define DEFAULT_FILE "file.txt"

void ksa(const unsigned char *key, size_t key_len, unsigned char *S) {
    for (int i = 0; i < 256; i++) {
        S[i] = (unsigned char)i;
    }
    int j = 0;
    for (int i = 0; i < 256; i++) {
        j = (j + S[i] + key[i % key_len]) % 256;
        unsigned char tmp = S[i];
        S[i] = S[j];
        S[j] = tmp;
    }
}

void prga(unsigned char *S, const unsigned char *data, unsigned char *out, size_t data_len) {
    unsigned char S_box[256];
    memcpy(S_box, S, 256);
    int i = 0, j = 0;
    for (size_t k = 0; k < data_len; k++) {
        i = (i + 1) % 256;
        j = (j + S_box[i]) % 256;
        unsigned char tmp = S_box[i];
        S_box[i] = S_box[j];
        S_box[j] = tmp;
        unsigned char keystream_byte = S_box[(S_box[i] + S_box[j]) % 256];
        out[k] = data[k] ^ keystream_byte;
    }
}

int encrypt_file(const char *filepath, const unsigned char *key, size_t key_len) {
    FILE *fp = fopen(filepath, "rb");
    if (!fp) {
        fprintf(stderr, "[-] Error: %s not found.\n", filepath);
        return 1;
    }

    fseek(fp, 0, SEEK_END);
    long file_size = ftell(fp);
    fseek(fp, 0, SEEK_SET);

    if (file_size < 0) {
        fclose(fp);
        return 1;
    }

    unsigned char *buffer = malloc(file_size > 0 ? file_size : 1);
    if (!buffer) {
        fclose(fp);
        return 1;
    }

    if (file_size > 0) {
        if (fread(buffer, 1, file_size, fp) != (size_t)file_size) {
            fclose(fp);
            free(buffer);
            return 1;
        }
    }
    fclose(fp);

    unsigned char S[256];
    ksa(key, key_len, S);

    unsigned char *ciphertext = malloc(file_size > 0 ? file_size : 1);
    if (!ciphertext) {
        free(buffer);
        return 1;
    }

    if (file_size > 0) {
        prga(S, buffer, ciphertext, file_size);
    }

    fp = fopen(filepath, "wb");
    if (!fp) {
        fprintf(stderr, "[-] Error opening %s for writing.\n", filepath);
        free(buffer);
        free(ciphertext);
        return 1;
    }

    if (file_size > 0) {
        fwrite(ciphertext, 1, file_size, fp);
    }
    fclose(fp);

    free(buffer);
    free(ciphertext);

    printf("[+] Successfully encrypted %s\n", filepath);
    return 0;
}

int main(int argc, char *argv[]) {
    const char *filepath = (argc > 1) ? argv[1] : DEFAULT_FILE;
    const char *key = (argc > 2) ? argv[2] : DEFAULT_KEY;

    return encrypt_file(filepath, (const unsigned char *)key, strlen(key));
}
