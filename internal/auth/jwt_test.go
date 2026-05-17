package auth

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestGenerateAndValidateToken(t *testing.T) {
	svc := NewAuthService("test-secret-key", 24)

	token, err := svc.GenerateToken(1, "pro")
	require.NoError(t, err)
	require.NotEmpty(t, token)

	claims, err := svc.ValidateToken(token)
	require.NoError(t, err)
	assert.Equal(t, 1, claims.UserID)
	assert.Equal(t, "pro", claims.PlanType)
	assert.Equal(t, "temu-tools", claims.Issuer)
}

func TestTokenExpired(t *testing.T) {
	svc := NewAuthService("test-secret", 0)

	token, err := svc.GenerateToken(1, "basic")
	require.NoError(t, err)

	_, err = svc.ValidateToken(token)
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "expired")
}

func TestInvalidToken(t *testing.T) {
	svc := NewAuthService("test-secret", 24)

	_, err := svc.ValidateToken("invalid-token-string")
	assert.Error(t, err)
}

func TestWrongSecret(t *testing.T) {
	svc1 := NewAuthService("secret-1", 24)
	svc2 := NewAuthService("secret-2", 24)

	token, err := svc1.GenerateToken(1, "pro")
	require.NoError(t, err)

	_, err = svc2.ValidateToken(token)
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "signature is invalid")
}

func TestMultipleTokens(t *testing.T) {
	svc := NewAuthService("test-secret", 24)

	tokens := make([]string, 3)
	for i := 0; i < 3; i++ {
		token, err := svc.GenerateToken(i+1, "enterprise")
		require.NoError(t, err)
		tokens[i] = token
	}

	for i, token := range tokens {
		claims, err := svc.ValidateToken(token)
		require.NoError(t, err)
		assert.Equal(t, i+1, claims.UserID)
	}
}

func TestPlanTypePreserved(t *testing.T) {
	svc := NewAuthService("test-secret", 24)

	planTypes := []string{"basic", "pro", "enterprise", "lifetime"}
	for _, plan := range planTypes {
		token, err := svc.GenerateToken(1, plan)
		require.NoError(t, err)

		claims, err := svc.ValidateToken(token)
		require.NoError(t, err)
		assert.Equal(t, plan, claims.PlanType)
	}
}
