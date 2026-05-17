package config

import (
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestLoadConfigWithDefaults(t *testing.T) {
	cfg := LoadConfig(".env.nonexistent")

	assert.Equal(t, 8080, cfg.Server.Port)
	assert.Equal(t, "0.0.0.0", cfg.Server.Address)
	assert.Equal(t, "release", cfg.Server.Mode)
	assert.Equal(t, 3306, cfg.Database.Port)
	assert.Equal(t, "localhost", cfg.Database.Host)
	assert.Equal(t, "root", cfg.Database.User)
	assert.Equal(t, "temu_tools", cfg.Database.DBName)
	assert.Equal(t, "global", cfg.Temu.Region)
}

func TestLoadConfigWithEnvVars(t *testing.T) {
	os.Setenv("TEMU_SERVER_PORT", "9090")
	os.Setenv("TEMU_SERVER_ADDRESS", "127.0.0.1")
	os.Setenv("TEMU_SERVER_MODE", "debug")
	defer func() {
		os.Unsetenv("TEMU_SERVER_PORT")
		os.Unsetenv("TEMU_SERVER_ADDRESS")
		os.Unsetenv("TEMU_SERVER_MODE")
	}()

	cfg := LoadConfig(".env.nonexistent")
	assert.Equal(t, 9090, cfg.Server.Port)
	assert.Equal(t, "127.0.0.1", cfg.Server.Address)
	assert.Equal(t, "debug", cfg.Server.Mode)
}

func TestDSN(t *testing.T) {
	cfg := &DatabaseConfig{
		Host:     "mysql.example.com",
		Port:     3307,
		User:     "admin",
		Password: "secret",
		DBName:   "temu_prod",
	}

	dsn := cfg.DSN()
	assert.Contains(t, dsn, "admin:secret@tcp(mysql.example.com:3307)/temu_prod")
	assert.Contains(t, dsn, "charset=utf8mb4")
	assert.Contains(t, dsn, "parseTime=True")
}

func TestDatabaseDefaults(t *testing.T) {
	cfg := &DatabaseConfig{
		Host:   "localhost",
		Port:   3306,
		User:   "root",
		DBName: "temu_tools",
	}

	dsn := cfg.DSN()
	assert.Contains(t, dsn, "root:@tcp(localhost:3306)/temu_tools")
}

func TestTemuConfigDefaults(t *testing.T) {
	cfg := LoadConfig(".env.nonexistent")

	assert.Equal(t, "global", cfg.Temu.Region)
	assert.Equal(t, "", cfg.Temu.AppKey)
	assert.Equal(t, "", cfg.Temu.AppSecret)
	assert.Equal(t, "", cfg.Temu.Proxy)
}

func TestServerConfigDefault(t *testing.T) {
	cfg := LoadConfig(".env.nonexistent")

	assert.Equal(t, "change-me-in-production", cfg.Auth.JWTSecret)
	assert.Equal(t, 24, cfg.Auth.TokenExpire)
	assert.Equal(t, "", cfg.Auth.AdminPassword)
}
