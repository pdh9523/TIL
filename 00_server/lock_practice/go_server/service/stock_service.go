package service

import (
	"go_server/repository"
	"gorm.io/gorm"
	"sync"
)

type StockService struct {
	repository *repository.StockRepository
	mutexes    map[int64]*sync.Mutex
	mutex      sync.Mutex
}

// NewStockService 는 StockService의 생성자 입니다.
func NewStockService(stockRepository *repository.StockRepository) *StockService {
	return &StockService{
		repository: stockRepository,
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

// DecreaseWithMutexLock 은 뮤텍스 락을 활용해 Decrease 과정에서의 경쟁 상태를 해소 합니다.
func (s *StockService) DecreaseWithMutexLock(id, quantity int64) error {
	lock := s.lockForID(id)
	lock.Lock()
	defer lock.Unlock()

	return s.Decrease(id, quantity)
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
