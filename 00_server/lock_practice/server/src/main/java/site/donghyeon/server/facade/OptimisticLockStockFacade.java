package site.donghyeon.server.facade;

import org.springframework.stereotype.Component;
import site.donghyeon.server.service.StockService;

@Component
public class OptimisticLockStockFacade {

    private final StockService stockService;

    public OptimisticLockStockFacade(StockService stockService) {
        this.stockService = stockService;
    }

    public int decrease(Long id, Long quantity) throws InterruptedException {
        int tryCount = 0;
        while (true) {
            try {
                stockService.decreaseWithOptimisticLock(id, quantity);
                break;
            } catch (Exception e) {
                tryCount++;
                Thread.sleep(50);
            }
        }
        return tryCount;
    }
}
