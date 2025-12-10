package repository

import (
	"gorm.io/gorm"
)

type LockRepository struct {
	db *gorm.DB
}

func NewLockRepository(db *gorm.DB) *LockRepository {
	return &LockRepository{
		db: db,
	}
}

// WithTxLock 은 트랜잭션을 생성하고, 입력된 키를 기준으로 중복을 막는다.
func (r *LockRepository) WithTxLock(
	key int64,
	fn func(tx *gorm.DB) error,
) error {
	return r.db.Transaction(func(tx *gorm.DB) error {
		if err := acquireAdvisoryTxLock(tx, key); err != nil {
			return err
		}
		return fn(tx)
	})
}

// acquireAdvisoryTxLock 은 "SELECT pg_advisory_xact_lock(key)" 쿼리로 postgres 에서 트랜잭션 락을 획득한다.
func acquireAdvisoryTxLock(tx *gorm.DB, key int64) error {
	var dummy string
	if err := tx.Raw("SELECT pg_advisory_xact_lock(?)", key).Scan(&dummy).Error; err != nil {
		return err
	}
	return nil
}
