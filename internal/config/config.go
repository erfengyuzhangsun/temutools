package config

import (
	"log/slog"
	"os"
	"strconv"

	"github.com/spf13/viper"
)

type Config struct {
	Server   ServerConfig
	Database DatabaseConfig
	Auth     AuthConfig
	Temu     TemuConfig
}

type ServerConfig struct {
	Port    int
	Address string
	Mode    string
}

type DatabaseConfig struct {
	Host     string
	Port     int
	User     string
	Password string
	DBName   string
}

type AuthConfig struct {
	JWTSecret     string
	TokenExpire   int
	AdminEmail    string
	AdminPassword string
}

type TemuConfig struct {
	AppKey    string
	AppSecret string
	Region    string
	Proxy     string
}

var Cfg *Config

func LoadConfig(path string) *Config {
	v := viper.New()
	v.SetConfigFile(path)
	v.AutomaticEnv()
	v.SetEnvPrefix("TEMU")

	if err := v.ReadInConfig(); err != nil {
		slog.Warn("config file not found, using env vars", "path", path, "error", err)
	}

	v.SetDefault("SERVER_PORT", 8080)
	v.SetDefault("SERVER_ADDRESS", "0.0.0.0")
	v.SetDefault("SERVER_MODE", "release")
	v.SetDefault("DB_PORT", 3306)
	v.SetDefault("DB_HOST", "localhost")
	v.SetDefault("DB_USER", "root")
	v.SetDefault("DB_NAME", "temu_tools")
	v.SetDefault("JWT_SECRET", "change-me-in-production")
	v.SetDefault("TOKEN_EXPIRE", 24)
	v.SetDefault("TEMU_API_REGION", "global")

	cfg := &Config{
		Server: ServerConfig{
			Port:    v.GetInt("SERVER_PORT"),
			Address: v.GetString("SERVER_ADDRESS"),
			Mode:    v.GetString("SERVER_MODE"),
		},
		Database: DatabaseConfig{
			Host:     getEnvOrDefault("DB_HOST", v.GetString("DB_HOST"), "localhost"),
			Port:     v.GetInt("DB_PORT"),
			User:     getEnvOrDefault("DB_USER", v.GetString("DB_USER"), "root"),
			Password: os.Getenv("DB_PASSWORD"),
			DBName:   getEnvOrDefault("DB_NAME", v.GetString("DB_NAME"), "temu_tools"),
		},
		Auth: AuthConfig{
			JWTSecret:     os.Getenv("JWT_SECRET"),
			TokenExpire:   v.GetInt("TOKEN_EXPIRE"),
			AdminEmail:    os.Getenv("ADMIN_EMAIL"),
			AdminPassword: os.Getenv("ADMIN_PASSWORD"),
		},
		Temu: TemuConfig{
			AppKey:    os.Getenv("TEMU_APP_KEY"),
			AppSecret: os.Getenv("TEMU_APP_SECRET"),
			Region:    v.GetString("TEMU_API_REGION"),
			Proxy:     os.Getenv("HTTPS_PROXY"),
		},
	}

	if cfg.Auth.JWTSecret == "" {
		cfg.Auth.JWTSecret = "change-me-in-production"
		slog.Warn("JWT_SECRET not set, using insecure default")
	}
	if cfg.Database.Password == "" {
		slog.Warn("DB_PASSWORD not set")
	}

	if cfg.Server.Mode == "debug" {
		slog.SetLogLoggerLevel(slog.LevelDebug)
	}

	Cfg = cfg
	return cfg
}

func (d *DatabaseConfig) DSN() string {
	return d.User + ":" + d.Password + "@tcp(" + d.Host + ":" + strconv.Itoa(d.Port) + ")/" + d.DBName + "?charset=utf8mb4&parseTime=True&loc=Local"
}

func getEnvOrDefault(key, vipVal, defaultVal string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	if vipVal != "" {
		return vipVal
	}
	return defaultVal
}
