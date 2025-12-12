package site.donghyeon.server.facade;

import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.support.TransactionSynchronization;
import org.springframework.transaction.support.TransactionSynchronizationManager;
import site.donghyeon.server.repository.LockRepository;
import site.donghyeon.server.service.StockService;

@Component
public class NamedLockStockFacade {

    private final LockRepository lockRepository;
    private final StockService stockService;

    public NamedLockStockFacade(LockRepository lockRepository, StockService stockService) {
        this.lockRepository = lockRepository;
        this.stockService = stockService;
    }

    @Transactional
    public void decreaseWithTransactionLock(Long id, Long quantity) {
        lockRepository.tryLock("stock: " + id);
        stockService.decreaseWithNamedLock(id, quantity);
    }

    @Transactional
    public void decreaseWithSessionLock(Long id, Long quantity) {
        lockRepository.getLock("stock: " + id);

        TransactionSynchronizationManager.registerSynchronization(
                new TransactionSynchronization() {
                    @Override
                    public void afterCommit() {
                        lockRepository.releaseLock("stock: " + id);
                    }
                }
        );

        stockService.decreaseWithNamedLock(id, quantity);
    }
}
