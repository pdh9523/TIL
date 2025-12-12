package repository

import (
	"errors"
	"go_server/domain"
	"gorm.io/gorm"
	"gorm.io/gorm/clause"
)

var ErrOptimisticLock = errors.New("낙관적 락 충돌 발생")

type StockRepository struct {
	db *gorm.DB
}

// NewStockRepository 은 레포지토리의 생성자입니다.
func NewStockRepository(db *gorm.DB) *StockRepository {
	return &StockRepository{
		db: db,
	}
}

// Transaction 은 전달된 fn 을 하나의 DB 트랜잭션 안에서 실행합니다.
// fn 이 nil을 반환하면 커밋하고, 에러를 반환하면 롤백합니다.
func (r *StockRepository) Transaction(fn func(tx *gorm.DB) error) error {
	return r.db.Transaction(fn)
}

// FindByIDTx 는 DB에서 특정 id를 PK로 가진 Stock 을 가져오고, 없는 경우 nil과 에러를 반환합니다.
func (r *StockRepository) FindByIDTx(tx *gorm.DB, id int64) (*domain.Stock, error) {
	var stock domain.Stock
	if err := tx.Where("id = ?", id).First(&stock).Error; err != nil {
		return nil, err
	}
	return &stock, nil
}

// FindByIDWithPessimisticLockTx 는 findByIdTx 에서 비관적 락을 적용한 메서드 입니다.
func (r *StockRepository) FindByIDWithPessimisticLockTx(tx *gorm.DB, id int64) (*domain.Stock, error) {
	var stock domain.Stock
	if err := tx.
		Clauses(clause.Locking{Strength: "UPDATE"}).
		Where("id = ?", id).
		First(&stock).Error; err != nil {
		return nil, err
	}
	return &stock, nil
}

// FindByID 는 FindByIDTx 에서 트랜잭션을 고려하지 않은 메서드입니다.
func (r *StockRepository) FindByID(id int64) (*domain.Stock, error) {
	return r.FindByIDTx(r.db, id)
}

// SaveTx 는 새로운, 또는 수정된 Stock 을 DB에 저장합니다.
func (r *StockRepository) SaveTx(tx *gorm.DB, stock *domain.Stock) error {
	return tx.Save(stock).Error
}

// SaveWithOptimisticLockTx 는 SaveTx 메서드에 낙관적 락을 적용한 메서드 입니다.
func (r *StockRepository) SaveWithOptimisticLockTx(tx *gorm.DB, stock *domain.Stock) error {
	res := tx.Model(stock).Where("version = ?", stock.Version).Updates(map[string]any{
		"quantity": stock.Quantity,
		"version":  gorm.Expr("version + ?", 1),
	})

	if res.Error != nil {
		return res.Error
	}
	if res.RowsAffected == 0 {
		return ErrOptimisticLock
	}
	return nil
}

// Save 는 SaveTx 에서 트랜잭션을 고려하지 않은 메서드입니다.
func (r *StockRepository) Save(stock *domain.Stock) error {
	return r.SaveTx(r.db, stock)
}

// DeleteByID 는 DB에서 특정 id를 PK로 가진 Stock 을 삭제하고, 오류 발생 시 에러를 반환합니다.
func (r *StockRepository) DeleteByID(id int64) error {
	return r.db.Delete(&domain.Stock{ID: id}).Error
}
