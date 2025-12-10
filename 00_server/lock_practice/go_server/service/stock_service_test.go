package service

import (
	"github.com/stretchr/testify/assert"
	"go_server/domain"
	"go_server/infra"
	"go_server/repository"
	"sync"
	"testing"
)

func TestStockService(t *testing.T) {
	dbConfig := infra.NewGormConfig()
	db, _ := dbConfig.NewGormDB()
	stockRepository := repository.NewStockRepository(db)
	lockRepository := repository.NewLockRepository(db)
	stockService := NewStockService(stockRepository, lockRepository)

	t.Run("재고 감소 테스트", func(t *testing.T) {
		err := stockRepository.Save(&domain.Stock{ID: 1, Quantity: 100})
		assert.NoError(t, err)

		err = stockService.Decrease(1, 1)
		assert.NoError(t, err)

		stock, err := stockRepository.FindByID(1)
		assert.NoError(t, err)
		assert.Equal(t, &domain.Stock{ID: 1, Quantity: 99}, stock)
	})

	t.Run("재고 동시 감소 테스트", func(t *testing.T) {
		err := stockRepository.Save(&domain.Stock{ID: 1, Quantity: 100})
		assert.NoError(t, err)

		var wg sync.WaitGroup
		errs := make(chan error, 100)
		for i := 0; i < 100; i++ {
			wg.Add(1)
			go func() {
				defer wg.Done()
				errs <- stockService.Decrease(1, 1)
			}()
		}
		wg.Wait()

		close(errs)
		for err := range errs {
			assert.NoError(t, err)
		}

		stock, err := stockRepository.FindByID(1)

		assert.NoError(t, err)
		assert.Equal(t, &domain.Stock{ID: 1, Quantity: 0}, stock)
	})

	t.Run("재고 동시 감소 테스트 - 뮤텍스 락", func(t *testing.T) {
		err := stockRepository.Save(&domain.Stock{ID: 1, Quantity: 100})
		assert.NoError(t, err)

		var wg sync.WaitGroup
		errs := make(chan error, 100)
		for i := 0; i < 100; i++ {
			wg.Add(1)
			go func() {
				defer wg.Done()
				errs <- stockService.DecreaseWithMutexLock(1, 1)
			}()
		}
		wg.Wait()

		close(errs)
		for err := range errs {
			assert.NoError(t, err)
		}

		stock, err := stockRepository.FindByID(1)

		assert.NoError(t, err)
		assert.Equal(t, &domain.Stock{ID: 1, Quantity: 0}, stock)
	})

	t.Run("재고 동시 감소 테스트 - 비관적 락", func(t *testing.T) {
		err := stockRepository.Save(&domain.Stock{ID: 1, Quantity: 100})
		assert.NoError(t, err)

		var wg sync.WaitGroup
		errs := make(chan error, 100)
		for i := 0; i < 100; i++ {
			wg.Add(1)
			go func() {
				defer wg.Done()
				errs <- stockService.DecreaseWithPessimisticLock(1, 1)
			}()
		}
		wg.Wait()

		close(errs)
		for err := range errs {
			assert.NoError(t, err)
		}

		stock, err := stockRepository.FindByID(1)

		assert.NoError(t, err)
		assert.Equal(t, &domain.Stock{ID: 1, Quantity: 0}, stock)
	})

	t.Run("재고 동시 감소 테스트 - 낙관적 락", func(t *testing.T) {
		err := stockRepository.Save(&domain.Stock{ID: 1, Quantity: 100})
		assert.NoError(t, err)

		var wg sync.WaitGroup
		errs := make(chan error, 100)
		for i := 0; i < 100; i++ {
			wg.Add(1)
			go func() {
				defer wg.Done()
				errs <- stockService.DecreaseWithOptimisticLock(1, 1)
			}()
		}
		wg.Wait()

		close(errs)
		for err := range errs {
			assert.NoError(t, err)
		}

		stock, err := stockRepository.FindByID(1)

		assert.NoError(t, err)
		assert.Equal(t, int64(0), stock.Quantity)
	})

	t.Run("재고 동시 감소 테스트 - 트랜잭션 락", func(t *testing.T) {
		err := stockRepository.Save(&domain.Stock{ID: 1, Quantity: 100})
		assert.NoError(t, err)

		var wg sync.WaitGroup
		errs := make(chan error, 100)
		for i := 0; i < 100; i++ {
			wg.Add(1)
			go func() {
				defer wg.Done()
				errs <- stockService.DecreaseWithTransactionLock(1, 1)
			}()
		}
		wg.Wait()

		close(errs)
		for err := range errs {
			assert.NoError(t, err)
		}

		stock, err := stockRepository.FindByID(1)

		assert.NoError(t, err)
		assert.Equal(t, int64(0), stock.Quantity)
	})
}
