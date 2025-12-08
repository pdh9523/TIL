package site.donghyeon.server.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import site.donghyeon.server.domain.Stock;

public interface StockRepository extends JpaRepository<Stock, Long> {
}
