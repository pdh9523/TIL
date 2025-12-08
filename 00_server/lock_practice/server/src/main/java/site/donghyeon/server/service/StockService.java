package site.donghyeon.server.service;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import site.donghyeon.server.domain.Stock;
import site.donghyeon.server.repository.StockRepository;

@Service
public class StockService {

    private final StockRepository stockRepository;

    public StockService(StockRepository stockRepository) {
        this.stockRepository = stockRepository;
    }

    @Transactional
    public void decrease(Long stockId, Long quantity) {
        Stock stock = stockRepository.findById(stockId).orElseThrow(RuntimeException::new);

        stock.decrease(quantity);

        stockRepository.save(stock);
    }

    @Transactional
    public synchronized void decreaseWithSynchronizedAndTransactional(Long stockId, Long quantity) {
        Stock stock = stockRepository.findById(stockId).orElseThrow(RuntimeException::new);

        stock.decrease(quantity);

        stockRepository.save(stock);
    }

    public synchronized void decreaseWithSynchronized(Long stockId, Long quantity) {
        Stock stock = stockRepository.findById(stockId).orElseThrow(RuntimeException::new);

        stock.decrease(quantity);

        stockRepository.save(stock);
    }

    @Transactional
    public void decreaseWithOptimisticLock(Long stockId, Long quantity) {
        Stock stock = stockRepository.findByIdWithOptimisticLock(stockId).orElseThrow(RuntimeException::new);

        stock.decrease(quantity);

        stockRepository.save(stock);
    }

    @Transactional
    public void decreaseWithPessimisticLock(Long stockId, Long quantity) {
        Stock stock = stockRepository.findByIdWithPessimisticLock(stockId).orElseThrow(RuntimeException::new);

        stock.decrease(quantity);

        stockRepository.save(stock);
    }
}
