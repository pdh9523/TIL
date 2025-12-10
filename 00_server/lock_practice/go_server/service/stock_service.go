package service

import (
	"go_server/repository"
	"gorm.io/gorm"
)

type StockService struct {
	repository *repository.StockRepository
}

// NewStockService 는 StockService의 생성자 입니다.
func NewStockService(stockRepository *repository.StockRepository) *StockService {
	return &StockService{
		repository: stockRepository,
	}
}

func (s *StockService) Decrease(id, quantity int64) error {
	return s.repository.Transaction(func(db *gorm.DB) error {
		stock, err := s.repository.FindByID(id)
		if err != nil {
			return err
		}
		if err := stock.Decrease(quantity); err != nil {
			return err
		}

		if err := s.repository.Save(stock); err != nil {
			return err
		}
		return nil
	})
}
