package service

import (
	"github.com/stretchr/testify/assert"
	"go_server/domain"
	"go_server/infra"
	"go_server/repository"
	"testing"
)

func TestStockService(t *testing.T) {
	dbConfig := infra.NewGormConfig()
	db, _ := dbConfig.NewGormDB()
	stockRepository := repository.NewStockRepository(db)
	stockService := NewStockService(stockRepository)

	t.Run("재고 감소 테스트", func(t *testing.T) {
		err := stockRepository.Save(&domain.Stock{ID: 1, Quantity: 100})
		assert.NoError(t, err)

		err = stockService.Decrease(1, 1)
		assert.NoError(t, err)

		stock, err := stockRepository.FindByID(1)
		assert.NoError(t, err)
		assert.Equal(t, &domain.Stock{ID: 1, Quantity: 99}, stock)

		_ = stockRepository.DeleteByID(stock.ID)
	})
}
