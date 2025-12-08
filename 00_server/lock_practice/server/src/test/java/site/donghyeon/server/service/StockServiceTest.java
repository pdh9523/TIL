package site.donghyeon.server.service;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import site.donghyeon.server.domain.Stock;
import site.donghyeon.server.repository.StockRepository;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class StockServiceTest {

    @Autowired
    private StockService stockService;

    @Autowired
    private StockRepository stockRepository;

    @BeforeEach
    public void beforeEach() {
        stockRepository.saveAndFlush(new Stock(100L));
    }

    @AfterEach
    public void afterEach() {
        stockRepository.deleteAll();
    }

    @Test
    public void 재고_감소() {
        stockService.decrease(1L, 1L);

        Stock stock = stockRepository.findById(1L).orElseThrow(RuntimeException::new);

        assertEquals(99, stock.getQuantity());
    }

    @Test
    public void 동시에_100개_요청() throws InterruptedException {
        int threadCount = 100;
        ExecutorService executorService = Executors.newFixedThreadPool(threadCount);
        CountDownLatch countDownLatch = new CountDownLatch(threadCount);

        for (int i=0; i<threadCount; i++) {
            executorService.submit(() -> {
                try {
                    stockService.decrease(1L, 1L);
                } finally {
                    countDownLatch.countDown();
                }
            });
        }
        countDownLatch.await();

        Stock stock = stockRepository.findById(1L).orElseThrow(RuntimeException::new);
        assertEquals(0, stock.getQuantity());
        /*
         Expected: 100 - (1 *100) = 0
         Actual: 88 ~ 92

         동시 조회로 인한 경쟁 상태, lost update 확인
         */
    }
}