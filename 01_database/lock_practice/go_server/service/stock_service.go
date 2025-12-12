package service

import (
	"go_server/repository"
	"gorm.io/gorm"
	"sync"
	"time"
)

type StockService struct {
	repository *repository.StockRepository
	lock       *repository.LockRepository
	mutexes    map[int64]*sync.Mutex
	mutex      sync.Mutex
}

// NewStockService 는 StockService의 생성자 입니다.
func NewStockService(
	stockRepository *repository.StockRepository,
	lockRepository *repository.LockRepository,
) *StockService {
	return &StockService{
		repository: stockRepository,
		lock:       lockRepository,
		mutexes:    make(map[int64]*sync.Mutex),
	}
}

// Decrease 는 ID를 PK로 가지는 재고를 조회하고, 값을 감소시키는 메서드입니다.
// 해당 과정은 한 트랜잭션으로 감싸져 있습니다.
func (s *StockService) Decrease(id, quantity int64) error {
	return s.repository.Transaction(func(db *gorm.DB) error {
		stock, err := s.repository.FindByIDTx(db, id)
		if err != nil {
			return err
		}
		if err := stock.Decrease(quantity); err != nil {
			return err
		}

		if err := s.repository.SaveTx(db, stock); err != nil {
			return err
		}
		return nil
	})
}

// DecreaseWithPessimisticLock 은 Decrease 에 비관적 락을 적용한 경우입니다.
func (s *StockService) DecreaseWithPessimisticLock(id, quantity int64) error {
	return s.repository.Transaction(func(db *gorm.DB) error {
		stock, err := s.repository.FindByIDWithPessimisticLockTx(db, id)
		if err != nil {
			return err
		}
		if err := stock.Decrease(quantity); err != nil {
			return err
		}

		if err := s.repository.SaveTx(db, stock); err != nil {
			return err
		}
		return nil
	})
}

// DecreaseWithMutexLock 은 뮤텍스 락을 활용해 Decrease 과정에서의 경쟁 상태를 해소 합니다.
func (s *StockService) DecreaseWithMutexLock(id, quantity int64) error {
	lock := s.lockForID(id)
	lock.Lock()
	defer lock.Unlock()

	return s.Decrease(id, quantity)
}

// DecreaseWithOptimisticLock 은 낙관적 락을 활용해 Decrease 과정에서의 경쟁 상태를 해소 합니다.
func (s *StockService) DecreaseWithOptimisticLock(id, quantity int64) error {
	for {
		if err := s.repository.Transaction(func(db *gorm.DB) error {
			stock, err := s.repository.FindByIDTx(db, id)
			if err != nil {
				return err
			}
			if err := stock.Decrease(quantity); err != nil {
				return err
			}

			if err := s.repository.SaveWithOptimisticLockTx(db, stock); err != nil {
				return err
			}
			return nil
		}); err == nil {
			return nil
		}
		time.Sleep(time.Millisecond * 50)
	}
}

// DecreaseWithOptimisticLock 은 postgres의 트랜잭션 락(advisory_xact_lock)을 활용해 Decrease 과정에서의 경쟁 상태를 해소 합니다.
func (s *StockService) DecreaseWithTransactionLock(id, quantity int64) error {
	return s.lock.WithTxLock(id, func(db *gorm.DB) error {
		stock, err := s.repository.FindByIDTx(db, id)
		if err != nil {
			return err
		}
		if err := stock.Decrease(quantity); err != nil {
			return err
		}

		if err := s.repository.SaveTx(db, stock); err != nil {
			return err
		}
		return nil
	})
}

// lockForID 는 특정 PK 값을 기준으로 락을 생성하고 해제하는 메서드 입니다.
// 해당 메서드에도 진입/해제 시 서비스 단위의 락이 발생해 직렬화를 보장합니다.
func (s *StockService) lockForID(id int64) *sync.Mutex {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	if m, exists := s.mutexes[id]; exists {
		return m
	}

	m := &sync.Mutex{}
	s.mutexes[id] = m
	return m
}
