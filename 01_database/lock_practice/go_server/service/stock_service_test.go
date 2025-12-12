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
		assert.Equal(t, int64(99), stock.Quantity)

		// 기본 테스트
		// Expected: 99
		// Actual: 99
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
		assert.NotEqual(t, int64(0), stock.Quantity)

		// 동시성을 고려하지 않은 상태에서의 재고 동시 감소 테스트
		// "NOT" Expected: 0
		// Actual: 80-85
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
		assert.Equal(t, int64(0), stock.Quantity)

		// 뮤텍스 락을 적용한 경우. 이는 java 에서 synchronized 를 적용한 것과 논리상 동일하다.
		// Expected: 0
		// Actual: 0
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
		assert.Equal(t, int64(0), stock.Quantity)

		// 비관적 락을 적용한 경우
		// Expected: 0
		// Actual: 0
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
		assert.Equal(t, int64(100), stock.Version)

		// 낙관적 락을 적용한 경우
		// Expected: 0
		// Actual: 0
		// Excepted Version: 100
		// Actual Version: 100
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

		// 트랜잭션 락을 적용한 경우
		// Expected: 0
		// Actual: 0
	})
}
