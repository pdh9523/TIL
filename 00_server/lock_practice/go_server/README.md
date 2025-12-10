

## 트러블 슈팅

- `트랜잭션 관련 메서드 수정` 커밋 이전에 테스트 구성 중 데드락 에러 발생

원인을 해당 코드에서 발견
```go
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
```
해당 코드는 `GORM` 이 트랜잭션을 위해 넘겨준 db를 사용하지 않고, 100개의 고루틴이 한 번에 `r.db` 를 통해 같은 row 에 진입하는 상황이 만들어짐

DB 레벨에서 락 경합이 심해져 문제가 발생했을 것이라 판단했고, `repository` 구조를 해당 커밋을 통해

```go
// FindByIDTx 는 DB에서 특정 id를 PK로 가진 Stock 을 가져오고, 없는 경우 nil과 에러를 반환합니다.
func (r *StockRepository) FindByIDTx(tx *gorm.DB, id int64) (*domain.Stock, error) {
	var stock domain.Stock
	if err := tx.Where("id = ?", id).First(&stock).Error; err != nil {
		return nil, err
	}
	return &stock, nil
}

// FindByID 는 FindByIDTx 에서 트랜잭션을 고려하지 않은 메서드입니다.
func (r *StockRepository) FindByID(id int64) (*domain.Stock, error) {
	return r.FindByIDTx(r.db, id)
}
```
`Tx` 함수를 먼저 정의하고, 트랜잭션을 고려하지 않은 버전을 별도로 구성하는 방식으로 변경해서 문제를 해결함