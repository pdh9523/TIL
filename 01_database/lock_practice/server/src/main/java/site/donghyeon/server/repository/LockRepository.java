package site.donghyeon.server.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import site.donghyeon.server.domain.Stock;

public interface LockRepository extends JpaRepository<Stock, Long> {
    @Query(value = "SELECT pg_advisory_xact_lock(hashtext(:key))", nativeQuery = true)
    void tryLock(String key);

    @Query(value = "SELECT pg_advisory_lock(hashtext(:key))", nativeQuery = true)
    void getLock(String key);

    @Query(value = "SELECT pg_advisory_unlock(hashtext(:key))", nativeQuery = true)
    void releaseLock(String key);
}
