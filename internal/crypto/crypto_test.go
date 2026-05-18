package crypto

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestEncryptDecrypt(t *testing.T) {
	key := []byte("this-is-a-32-byte-key-for-aes-256!!")
	plaintext := "admin@jinpuhuang.com"

	encrypted, err := EncryptString(plaintext, key)
	require.NoError(t, err)
	require.NotEmpty(t, encrypted)
	assert.NotEqual(t, plaintext, encrypted)

	decrypted, err := DecryptString(encrypted, key)
	require.NoError(t, err)
	assert.Equal(t, plaintext, decrypted)
}

func TestEncryptDecrypt_Empty(t *testing.T) {
	key := []byte("this-is-a-32-byte-key-for-aes-256!!")

	encrypted, err := EncryptString("", key)
	require.NoError(t, err)
	assert.Empty(t, encrypted)

	decrypted, err := DecryptString("", key)
	require.NoError(t, err)
	assert.Empty(t, decrypted)
}

func TestEncryptDecrypt_Unicode(t *testing.T) {
	key := []byte("this-is-a-32-byte-key-for-aes-256!!")
	plaintext := "测试微信昵称 🐋"

	encrypted, err := EncryptString(plaintext, key)
	require.NoError(t, err)

	decrypted, err := DecryptString(encrypted, key)
	require.NoError(t, err)
	assert.Equal(t, plaintext, decrypted)
}

func TestEncrypt_DifferentCiphertexts(t *testing.T) {
	key := []byte("this-is-a-32-byte-key-for-aes-256!!")
	plaintext := "same-text"

	e1, _ := EncryptString(plaintext, key)
	e2, _ := EncryptString(plaintext, key)
	assert.NotEqual(t, e1, e2, "AES-GCM with random nonce should produce different ciphertexts each time")
}

func TestDecrypt_WrongKey(t *testing.T) {
	key1 := []byte("this-is-a-32-byte-key-for-aes-256!!")
	key2 := []byte("this-is-a-different-32-byte-key-for-te!!")
	plaintext := "secret-data"

	encrypted, err := EncryptString(plaintext, key1)
	require.NoError(t, err)

	_, err = DecryptString(encrypted, key2)
	assert.Error(t, err)
}

func TestDecrypt_InvalidBase64(t *testing.T) {
	key := []byte("this-is-a-32-byte-key-for-aes-256!!")
	_, err := DecryptString("not-valid-base64!!!", key)
	assert.Error(t, err)
}

func TestValidateKey_ShortKey(t *testing.T) {
	key := []byte("short")
	plaintext := "data"

	encrypted, err := EncryptString(plaintext, key)
	require.NoError(t, err)

	decrypted, err := DecryptString(encrypted, key)
	require.NoError(t, err)
	assert.Equal(t, plaintext, decrypted)
}

func TestValidateKey_EmptyKey(t *testing.T) {
	_, err := EncryptString("data", []byte{})
	assert.ErrorIs(t, err, ErrInvalidKey)
}
