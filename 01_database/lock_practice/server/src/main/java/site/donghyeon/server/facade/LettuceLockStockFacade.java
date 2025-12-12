package site.donghyeon.server.facade;

import org.springframework.stereotype.Component;
import site.donghyeon.server.repository.RedisLockRepository;
import site.donghyeon.server.service.StockService;

@Component
public class LettuceLockStockFacade {

    private RedisLockRepository redisLockRepository;
    private StockService stockService;

    public LettuceLockStockFacade(RedisLockRepository redisLockRepository, StockService stockService) {
        this.redisLockRepository = redisLockRepository;
        this.stockService = stockService;
    }

    public void decrease(Long id, Long quantity) throws InterruptedException {
        while (!redisLockRepository.lock(id)) {
            Thread.sleep(100);
        }

        try {
            stockService.decreaseWithLettuceLock(id, quantity);
        } finally {
            redisLockRepository.unlock(id);
        }
    }
}
