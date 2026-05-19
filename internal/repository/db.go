package repository

import (
	"fmt"
	"log/slog"
	"sync"
	"time"

	_ "github.com/go-sql-driver/mysql"
	"gorm.io/driver/mysql"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"

	"github.com/erfengyuzhangsun/temutools/internal/config"
	"github.com/erfengyuzhangsun/temutools/internal/models"
)

var (
	db   *gorm.DB
	once sync.Once
)

func InitDB(cfg config.DatabaseConfig) (*gorm.DB, error) {
	var initErr error
	once.Do(func() {
		dsn := cfg.DSN()
		slog.Info("connecting to database", "host", cfg.Host, "port", cfg.Port, "db", cfg.DBName)

		gormConfig := &gorm.Config{
			Logger: logger.Default.LogMode(logger.Warn),
			NowFunc: func() time.Time {
				return time.Now()
			},
		}

		conn, err := gorm.Open(mysql.Open(dsn), gormConfig)
		if err != nil {
			initErr = fmt.Errorf("failed to connect to database: %w", err)
			return
		}

		sqlDB, err := conn.DB()
		if err != nil {
			initErr = fmt.Errorf("failed to get underlying sql.DB: %w", err)
			return
		}

		sqlDB.SetMaxOpenConns(50)
		sqlDB.SetMaxIdleConns(10)
		sqlDB.SetConnMaxLifetime(30 * time.Minute)
		sqlDB.SetConnMaxIdleTime(5 * time.Minute)

		db = conn
		slog.Info("database connected successfully")
	})

	return db, initErr
}

func GetDB() *gorm.DB {
	return db
}

func AutoMigrate() error {
	if db == nil {
		return fmt.Errorf("database not initialized")
	}

	slog.Info("running auto migration")

	db.Exec("SET FOREIGN_KEY_CHECKS = 0")

	if err := db.AutoMigrate(
		&models.User{},
		&models.Shop{},
		&models.ShopCredential{},
		&models.ProfitStat{},
		&models.SkuProfit{},
		&models.PricingLog{},
		&models.SyncRecord{},
		&models.TaskDefinition{},
		&models.SchedulerTask{},
		&models.SchedulerLog{},
		&models.FactoryProduct{},
		&models.Supplier{},
		&models.Order{},
		&models.SettlementRecord{},
	); err != nil {
		db.Exec("SET FOREIGN_KEY_CHECKS = 1")
		return err
	}

	db.Exec("SET FOREIGN_KEY_CHECKS = 1")

	migrator := db.Migrator()

	if migrator.HasColumn(&models.User{}, "access_password") {
		slog.Info("dropping deprecated column: access_password")
		if err := migrator.DropColumn(&models.User{}, "access_password"); err != nil {
			return fmt.Errorf("drop access_password column: %w", err)
		}
	}

	if !migrator.HasColumn(&models.User{}, "email") {
		slog.Info("adding missing column: email")
		if err := db.Exec("ALTER TABLE temu_users ADD COLUMN email VARCHAR(255) NOT NULL DEFAULT '' AFTER user_id, ADD UNIQUE INDEX idx_email (email)").Error; err != nil {
			return fmt.Errorf("add email column: %w", err)
		}
		db.Exec("UPDATE temu_users SET email = CONCAT('user_', user_id, '@legacy.com') WHERE email = ''")
	}

	if !migrator.HasColumn(&models.User{}, "password_hash") {
		slog.Info("adding missing column: password_hash")
		if err := db.Exec("ALTER TABLE temu_users ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT '' AFTER email").Error; err != nil {
			return fmt.Errorf("add password_hash column: %w", err)
		}
	}

	if err := db.Exec("ALTER TABLE temu_users MODIFY COLUMN start_date DATE NULL, MODIFY COLUMN expire_date DATE NULL").Error; err != nil {
		slog.Warn("alter start_date/expire_date nullable failed (may already be nullable)", "error", err)
	}

	return nil
}

func Close() error {
	if db != nil {
		sqlDB, err := db.DB()
		if err != nil {
			return err
		}
		return sqlDB.Close()
	}
	return nil
}
