package domain

import "errors"

type Stock struct {
	ID       int64 `gorm:"primaryKey:size:36"`
	Quantity int64 `gorm:"not null"`
	Version  int64 `gorm:"not null;default:0;version"`
}

// NewStock 은 Stock 의 생성자 입니다.
func NewStock(quantity int64) *Stock {
	return &Stock{
		Quantity: quantity,
	}
}

// TableName 은 gorm 에 의해 자동 실행되며, 테이블명을 stock 으로 설정합니다.
func (*Stock) TableName() string {
	return "stock"
}

// Decrease 은 Stock 의 재고를 감소시키는 메서드입니다.
func (s *Stock) Decrease(quantity int64) error {
	if quantity > s.Quantity {
		return errors.New("재고는 0개 미만이 될 수 없습니다.")
	}
	s.Quantity -= quantity
	return nil
}
