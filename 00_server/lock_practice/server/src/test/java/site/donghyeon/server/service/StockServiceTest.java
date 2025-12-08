package site.donghyeon.server.service;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import site.donghyeon.server.domain.Stock;
import site.donghyeon.server.facade.LettuceLockStockFacade;
import site.donghyeon.server.facade.NamedLockStockFacade;
import site.donghyeon.server.facade.OptimisticLockStockFacade;
//import site.donghyeon.server.facade.RedissonLockStockFacade;
import site.donghyeon.server.repository.StockRepository;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class StockServiceTest {

//    @Autowired
//    private RedissonLockStockFacade redissonLockStockFacade;

    @Autowired
    private LettuceLockStockFacade lettuceLockStockFacade;

    @Autowired
    private NamedLockStockFacade namedLockStockFacade;

    @Autowired
    private OptimisticLockStockFacade optimisticLockStockFacade;

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

    @Test
    public void 동시에_100개_요청_비관적_락() throws InterruptedException {
        int threadCount = 100;
        ExecutorService executorService = Executors.newFixedThreadPool(threadCount);
        CountDownLatch countDownLatch = new CountDownLatch(threadCount);
        for (int i=0; i<threadCount; i++) {
            executorService.submit(() -> {
                try {
                    stockService.decreaseWithPessimisticLock(1L, 1L);
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
        비관적 락을 통해 문제를 해결했다.

        - 기본 정의
        비관적 락: 충돌 상황을 가정하고, 일단 선점하면 다른 요청은 대기/차단하는 방식이다.
        SELECT ~ FOR UPDATE 구문으로 구현되며, DB가 로우 단위로 락을 잡고 직렬화된 순서로 처리한다.

        - 발생 문제
        낙관적 락으로 인해 발생하는 재시도 문제를 해결할 수 있지만, 분산 데이터베이스 상황에서는 해당 락만을 적용하기 어렵다.

        - 정리
        DB락은 단일 DB에서만 적용할 수 있다.
         */
    }

    @Test
    public void 동시에_100개_요청_트랜잭션_락() throws InterruptedException {
        int threadCount = 100;
        ExecutorService executorService = Executors.newFixedThreadPool(threadCount);
        CountDownLatch countDownLatch = new CountDownLatch(threadCount);
        for (int i=0; i<threadCount; i++) {
            executorService.submit(() -> {
                try {
                    namedLockStockFacade.decreaseWithTransactionLock(1L, 1L);
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
        네임드 락 중, 트랜잭션 락 형태로 해결했다.

        - 기본 정의
        트랜잭션 락: 네임드 락의 한 형태로, 임의의 키를 기준으로 트랜잭션 간 동시성을 제어한다.
        postgres 기준으로는 pg_advisory_lock을 호출 시, 현재 트랜잭션이 해당 키에 대한 락을 획득하고,
        트랜잭션이 커밋/롤백될 때 락이 해제된다.

        - 발생 문제
        동일 키에 대한 요청이 많을 경우, 후행 트랜잭션이 모두 락 획득 지점에서 대기해서 락 경합이 커질 수 있다.
        하나의 트랜잭션에서 여러 키에 대해 트랜잭션 락을 획득하는 경우, 락 획득 순서 차이에 의해 데드락이 발생할 수 있다.
        여전히 분산 환경에서는 일관성을 보장하지 않는다.

        - 정리
        트랜잭션과 락 생명주기가 맞아 떨어지기에 단순하고 직관적이다.
         */
    }

    @Test
    public void 동시에_100개_요청_세션_락() throws InterruptedException {
        int threadCount = 100;
        ExecutorService executorService = Executors.newFixedThreadPool(threadCount);
        CountDownLatch countDownLatch = new CountDownLatch(threadCount);
        for (int i=0; i<threadCount; i++) {
            executorService.submit(() -> {
                try {
                    namedLockStockFacade.decreaseWithSessionLock(1L, 1L);
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
        네임드 락 중, 세션 락 형태로 해결했다.

        - 기본 정의
        세션 락: 네임드 락 중, 세션(커넥션) 스코프에서 작동하는 락이다.
        postgres 기준으로 pg_advisory_lock을 호출 시, 현재 세션이 해당 키에 대한 락을 획득하고,
        동일 세션에서 pg_advisory_unlock을 호출하거나, 커넥션이 끊어질 때까지 유지된다.

        - 발생 문제
        세션 락 트러블 슈팅:

        @Transactional
        public void decrease(Long id, Long quantity) {
            lockRepository.getLock("stock: "+id);
            stockService.decreaseWithNamedLock(id, quantity);
            lockRepository.releaseLock("stock: "+id);
        }

        여기서 pg_advisory_lock - pg_advisory_unlock을 통해 네임드락을 구현하려고 했으나 실패했다.
        지금 트랜잭션 순서는 "락 획득 -> ( read - modify - write ) -> 락 해제 -> 트랜잭션 커밋" 이다.
        여기서 세션 락은 커밋과 무관하게 먼저 풀리기 때문에, 커밋되기 전에 다른 트랜잭션이 이전 스냅샷을 기준으로 갱신할 수 있다.
        따라서, 세션 락을 사용할 때는 비즈니스 로직이 커밋된 이후에 락이 해제되도록 강제(afterCommit)해야 한다.

        - 정리
        세션 락은 트랜잭션과 독립적인, 더 넓은 범위의 네임드 락을 제공하지만 @Transactional과 함께 사용할 때는 정합성 문제가 발생할 수 있다.
        그리고, 실무에서는 위의 트랜잭션 락(pg_advisory_xact_lock)을 사용해 구현하는 것이 더 단순하고 직관적이다.

         */
    }

    @Test
    public void 동시에_100개_요청_Lettuce() throws InterruptedException {
        int threadCount = 100;
        ExecutorService executorService = Executors.newFixedThreadPool(threadCount);
        CountDownLatch countDownLatch = new CountDownLatch(threadCount);
        for (int i=0; i<threadCount; i++) {
            executorService.submit(() -> {
                try {
                    lettuceLockStockFacade.decrease(1L, 1L);
                } catch (Exception e) {
                    throw new RuntimeException(e);
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
        Lettuce를 활용해, 분산 락을 구현해 해결했다.

        - 기본 정의
        분산 락: 여러 프로세스 / 여러 서버 인스턴스가 같은 공유 자원을 동시에 수정하지 않도록
        외부 공용 저장소 (여기서는 Redis)에 "락 정보"를 저장해 동시성을 제어한다.

        - 발생 문제
        분산 락은 네트워크 왕복 + Redis I/O가 항상 수반되므로 단일 DB 락이나 JVM 내 락보다 오버헤드가 크다.
        그리고 단순 구현 형태에서는 지금과 같이 스핀 락 형태(락이 잡힐 때까지 계속 재시도)가 되기 쉬운데,
        이 경우 충돌이 많은 구간에서 Redis 에 지속적으로 요청을 보내 Redis 서버에 부하를 줄 수 있다.

        - 정리
        여러 인스턴스와 여러 프로세스에 걸친 동시성을 제어해야할 때 유용하다.
        하지만, 오버헤드 비용이 크게 차이나기에 다중 인스턴스 및 서비스 간 조율이 꼭 필요한 경우에서만 신중하게 도입할 필요가 있다.
         */
    }

//    @Test
//    public void 동시에_100개_요청_Redisson() throws InterruptedException {
//        int threadCount = 100;
//        ExecutorService executorService = Executors.newFixedThreadPool(threadCount);
//        CountDownLatch countDownLatch = new CountDownLatch(threadCount);
//        for (int i=0; i<threadCount; i++) {
//            executorService.submit(() -> {
//                try {
//                    redissonLockStockFacade.decrease(1L, 1L);
//                } catch (Exception e) {
//                    throw new RuntimeException(e);
//                } finally {
//                    countDownLatch.countDown();
//                }
//            });
//        }
//        countDownLatch.await();
//
//        Stock stock = stockRepository.findById(1L).orElseThrow(RuntimeException::new);
//        assertEquals(0, stock.getQuantity());
//        /*
//
//        - 해결
//        Redisson pub/sub 을 활용해 락 구현을 구성했다.
//
//        - 기본 정의
//        분산 락:
//
//        - 발생 문제
//          2025.12.08 기준 테스트를 spring boot 4.0.0 버전에서 진행하고 있는데,
//          redisson-spring-boot-starter:3.52.0 가 최신버전이고, 이는 아직 spring boot 4.0.0과 호환되지 않는다.
//
//        - 정리
//          검증 보류
//         */
//    }
}