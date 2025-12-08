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

    @Test
    public void 동시에_100개_요청_synchronized_transactional() throws InterruptedException {
        int threadCount = 100;
        ExecutorService executorService = Executors.newFixedThreadPool(threadCount);
        CountDownLatch countDownLatch = new CountDownLatch(threadCount);

        for (int i=0; i<threadCount; i++) {
            executorService.submit(() -> {
                try {
                    stockService.decreaseWithSynchronizedAndTransactional(1L, 1L);
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
         Actual: 22-49

        - 기본 정의
        synchronized가 보장해 주는 것: 같은 JVM 안에서 이 메서드에 스레드가 동시에 둘 이상 들어오지 못한다.
        @Transactional이 실제로 동작하는 방식: 프록시 레벨에서 트랜잭션 시작 - {메서드 호출} - 트랜잭션 종료 흐름을 생성

        - 원인
        synchronized가 잡고 있는 범위는 타켓 메서드 본문 까지고,
        트랜잭션의 생명주기는 프록시에서 시작 - 종료 까지의 전체 흐름이다.

        - 발생 문제
        첫 번째 스레드가 트랜잭션 A를 시작해 synchronized 블록 안에서 find-update-write를 한 뒤 블록을 빠져나온 뒤에 커밋한다.
        블록을 빠져나온 뒤 ~ 커밋 사이의 간격에서 새로운 트랜잭션 B가 시작될 수 있고, 이로 인해 중복 읽기가 발생한다.

        - 정리
        synchronized로 메서드 실행은 직렬화했지만, 트랜잭션 시작/종료 시점이 바깥에 있기 때문에 완벽히 제어할 수 없다.
         */
    }
}