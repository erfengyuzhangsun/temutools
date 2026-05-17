package main

import (
	"context"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"

	"github.com/erfengyuzhangsun/temutools/internal/api"
	"github.com/erfengyuzhangsun/temutools/internal/auth"
	"github.com/erfengyuzhangsun/temutools/internal/config"
	"github.com/erfengyuzhangsun/temutools/internal/repository"
	"github.com/erfengyuzhangsun/temutools/internal/scheduler"
)

func main() {
	cfg := config.LoadConfig(".env")

	slog.Info("starting temu-tools-go server",
		"port", cfg.Server.Port,
		"mode", cfg.Server.Mode,
	)

	authService := auth.NewAuthService(cfg.Auth.JWTSecret, cfg.Auth.TokenExpire)

	db, err := repository.InitDB(cfg.Database)
	if err != nil {
		slog.Warn("database connection failed, running without DB", "error", err)
	} else {
		slog.Info("database connected")
		sqlDB, _ := db.DB()
		if err := sqlDB.Ping(); err == nil {
			if migrateErr := repository.AutoMigrate(); migrateErr != nil {
				slog.Warn("auto migration failed", "error", migrateErr)
			} else {
				repository.SeedAdmin(cfg.Auth.AdminEmail, cfg.Auth.AdminPassword)
			}
		}
	}

	sch := scheduler.New()
	scheduler.RegisterPresetTasks(sch, 1)
	sch.Start()

	router := api.SetupRouter(authService)

	router.Use(func(c *gin.Context) {
		c.Set("auth_service", authService)
		c.Set("scheduler", sch)
		c.Next()
	})

	addr := fmt.Sprintf("%s:%d", cfg.Server.Address, cfg.Server.Port)
	slog.Info("server listening", "address", addr)

	srv := &http.Server{
		Addr:    addr,
		Handler: router,
	}

	go func() {
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			slog.Error("server failed to start", "error", err)
			os.Exit(1)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	slog.Info("shutting down server...")

	sch.Stop()

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		slog.Error("server forced to shutdown", "error", err)
	}

	if db != nil {
		if sqlDB, err := db.DB(); err == nil {
			sqlDB.Close()
		}
	}

	slog.Info("server exited gracefully")
}
