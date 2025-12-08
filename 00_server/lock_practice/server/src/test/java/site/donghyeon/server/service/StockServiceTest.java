package site.donghyeon.server.service;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import site.donghyeon.server.domain.Stock;
import site.donghyeon.server.facade.OptimisticLockStockFacade;
import site.donghyeon.server.repository.StockRepository;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class StockServiceTest {

    @Autowired
    private OptimisticLockStockFacade  optimisticLockStockFacade;

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

    @Test
    public void 동시에_100개_요청_synchronized() throws InterruptedException {
        int threadCount = 100;
        ExecutorService executorService = Executors.newFixedThreadPool(threadCount);
        CountDownLatch countDownLatch = new CountDownLatch(threadCount);

        for (int i=0; i<threadCount; i++) {
            executorService.submit(() -> {
                try {
                    stockService.decreaseWithSynchronized(1L, 1L);
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
         Actual: 0

        - 해결
        위의 상황에서 문제는 커밋 시점이기에, 커밋 시점을 조절하면 문제가 사라진다.
        단일 서버에서는 이를 @Transactional을 제거함으로써 해결할 수 있다.

        - 발생 문제
        실서비스에서 단일 인스턴스, 단일 서버를 유지하는 경우는 거의 없다.

        - 정리
        서비스/서버 레벨에서 정의하는 것 뿐만 아니라 DB 자체에서도 접근 제어가 필요하다.
         */
    }

    @Test
    public void 동시에_100개_요청_낙관적_락() throws InterruptedException {
        int threadCount = 100;
        ExecutorService executorService = Executors.newFixedThreadPool(threadCount);
        CountDownLatch countDownLatch = new CountDownLatch(threadCount);
        AtomicInteger tryCount = new AtomicInteger();
        for (int i=0; i<threadCount; i++) {
            executorService.submit(() -> {
                try {
                    tryCount.addAndGet(optimisticLockStockFacade.decrease(1L, 1L));
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                } finally {
                    countDownLatch.countDown();
                }
            });
        }
        countDownLatch.await();

        Stock stock = stockRepository.findById(1L).orElseThrow(RuntimeException::new);
        assertEquals(0, stock.getQuantity());

        System.out.printf("tryCount: %d \n", tryCount.get());
        /*
         Expected: 100 - (1 *100) = 0
         Actual: 0
         tryCount: 380

        - 해결
        낙관적 락을 구현해 문제를 해결했다.

        - 기본 정의
        낙관적 락: 충돌이 나지 않음을 가정하고, 일단 자유롭게 수정하게 둔 뒤, 나중에 충돌이 났는지 확인해서 실패/재시도 하는 방식
        JPA 에서는 @Version 컬럼을 통해 버전을 관리하면서 이미 누가 먼저 수정해서 버전이 달라졌다면 에러를 발생시킨다.
        충돌이 드물면 성능과 확장성이 좋지만, 충돌 시 재시도/실패 처리 로직이 필요하다.
        쓰기 작업이 드물고 읽기 작업이 많은 경우 유효한 방식이다.

        - 발생 문제
        낙관적 락으로 문제를 해결할 수 있으나, 실제 요청은 100건이지만 재시도 로직으로 인해 총 380건의 트랜잭션 시도가 발생했고,
        테스트 시간 또한 가장 오래 걸렸다.

        - 정리
        지금처럼 쓰기 작업이 빈번한 경우 낙관적 락은 재시도 오버헤드로 인해 성능상 약점이 존재한다.
         */
    }
}