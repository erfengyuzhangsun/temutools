package auth

import (
	"fmt"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

type Claims struct {
	UserID   int    `json:"user_id"`
	PlanType string `json:"plan_type"`
	jwt.RegisteredClaims
}

type AuthService struct {
	secret      string
	tokenExpire time.Duration
}

func NewAuthService(secret string, expireHours int) *AuthService {
	return &AuthService{
		secret:      secret,
		tokenExpire: time.Duration(expireHours) * time.Hour,
	}
}

func (s *AuthService) GenerateToken(userID int, planType string) (string, error) {
	claims := &Claims{
		UserID:   userID,
		PlanType: planType,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(s.tokenExpire)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			Issuer:    "temu-tools",
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(s.secret))
}

func (s *AuthService) ValidateToken(tokenStr string) (*Claims, error) {
	token, err := jwt.ParseWithClaims(tokenStr, &Claims{}, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}
		return []byte(s.secret), nil
	})

	if err != nil {
		return nil, fmt.Errorf("invalid token: %w", err)
	}

	claims, ok := token.Claims.(*Claims)
	if !ok || !token.Valid {
		return nil, fmt.Errorf("invalid token claims")
	}

	return claims, nil
}
