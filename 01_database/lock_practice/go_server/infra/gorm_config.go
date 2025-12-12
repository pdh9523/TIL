package infra

import (
	"fmt"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

type GormConfig struct {
	Host         string
	Port         string
	Database     string
	Username     string
	Password     string
	SSLMode      string
	MaxOpenConns int
	MaxIdleConns int
}

// NewGormConfig 은 기설정된 DB 설정을 가져옵니다.
func NewGormConfig() *GormConfig {
	return &GormConfig{
		Host:         "localhost",
		Port:         "5432",
		Database:     "stock-practice",
		Username:     "admin",
		Password:     "1234",
		SSLMode:      "disable",
		MaxOpenConns: 10,
		MaxIdleConns: 10,
	}
}

// NewGormDB 은 Gorm DB 초기화 합니다.
// 현재 driver는 postgres로 설정되어 있습니다.
func (g *GormConfig) NewGormDB() (*gorm.DB, error) {
	logLevel := logger.Info
	gormConfig := gorm.Config{
		Logger: logger.Default.LogMode(logLevel),
	}

	db, err := gorm.Open(postgres.Open(g.DSN()), &gormConfig)
	if err != nil {
		return nil, err
	}

	sqlDB, err := db.DB()
	if err != nil {
		return nil, err
	}

	if g.MaxOpenConns > 0 {
		sqlDB.SetMaxOpenConns(g.MaxOpenConns)
	}
	if g.MaxIdleConns > 0 {
		sqlDB.SetMaxIdleConns(g.MaxIdleConns)
	}

	return db, nil
}

// DSN 은 DB 주소를 문자열로 파싱하는 헬퍼 메서드 입니다.
func (g *GormConfig) DSN() string {
	return fmt.Sprintf(
		"host=%s user=%s password=%s dbname=%s port=%s sslmode=%s TimeZone=Asia/Seoul",
		g.Host, g.Username, g.Password, g.Database, g.Port, g.SSLMode,
	)
}
