package crypto

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"encoding/base64"
	"errors"
	"fmt"
	"io"
	"os"
)

var ErrInvalidKey = errors.New("encryption key must be at least 1 byte")

func encryptionKey() []byte {
	return []byte(os.Getenv("ENCRYPTION_KEY"))
}

func validateKey(key []byte) ([]byte, error) {
	if len(key) == 0 {
		return nil, ErrInvalidKey
	}
	if len(key) < 32 {
		padded := make([]byte, 32)
		copy(padded, key)
		return padded, nil
	}
	return key[:32], nil
}

func Encrypt(plaintext, key []byte) (string, error) {
	k, err := validateKey(key)
	if err != nil {
		return "", err
	}

	block, err := aes.NewCipher(k)
	if err != nil {
		return "", fmt.Errorf("aes cipher: %w", err)
	}

	aesGCM, err := cipher.NewGCM(block)
	if err != nil {
		return "", fmt.Errorf("gcm: %w", err)
	}

	nonce := make([]byte, aesGCM.NonceSize())
	if _, err := io.ReadFull(rand.Reader, nonce); err != nil {
		return "", fmt.Errorf("nonce: %w", err)
	}

	ciphertext := aesGCM.Seal(nonce, nonce, plaintext, nil)
	return base64.StdEncoding.EncodeToString(ciphertext), nil
}

func Decrypt(encoded string, key []byte) ([]byte, error) {
	k, err := validateKey(key)
	if err != nil {
		return nil, err
	}

	ciphertext, err := base64.StdEncoding.DecodeString(encoded)
	if err != nil {
		return nil, fmt.Errorf("base64 decode: %w", err)
	}

	block, err := aes.NewCipher(k)
	if err != nil {
		return nil, fmt.Errorf("aes cipher: %w", err)
	}

	aesGCM, err := cipher.NewGCM(block)
	if err != nil {
		return nil, fmt.Errorf("gcm: %w", err)
	}

	nonceSize := aesGCM.NonceSize()
	if len(ciphertext) < nonceSize {
		return nil, errors.New("ciphertext too short")
	}

	nonce, ciphertext := ciphertext[:nonceSize], ciphertext[nonceSize:]
	plaintext, err := aesGCM.Open(nil, nonce, ciphertext, nil)
	if err != nil {
		return nil, fmt.Errorf("decrypt: %w", err)
	}

	return plaintext, nil
}

func EncryptString(plaintext string, key []byte) (string, error) {
	if plaintext == "" {
		return "", nil
	}
	return Encrypt([]byte(plaintext), key)
}

func DecryptString(encoded string, key []byte) (string, error) {
	if encoded == "" {
		return "", nil
	}
	decrypted, err := Decrypt(encoded, key)
	if err != nil {
		return "", err
	}
	return string(decrypted), nil
}

func EncryptPII(plaintext string) (string, error) {
	return EncryptString(plaintext, encryptionKey())
}

func DecryptPII(encoded string) (string, error) {
	return DecryptString(encoded, encryptionKey())
}
