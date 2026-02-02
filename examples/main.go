package main

import (
	"cache"
	"context"
	"fmt"
	"log"
	"time"
)

func main() {
	ctx := context.Background()

	cache1, err := cache.New(cache.Config{
		RedisAddr: "127.0.0.1:6379",
		Channel:   "distributed-cache",
	})
	if err != nil {
		log.Fatalf("Error creating cache: %v", err)
	}

	cache2, err := cache.New(cache.Config{
		RedisAddr: "127.0.0.1:6379",
		Channel:   "distributed-cache",
	})
	if err != nil {
		log.Fatalf("Error creating cache: %v", err)
	}

	fmt.Println("=== Test 1: Set on cache1, check invalidation on cache2 ===")

	// cache2 에 값 설정
	cache2.Set("user:1", "old-value")
	time.Sleep(100 * time.Millisecond) // ristretto 비동기 처리 대기

	// cache1에서 같은 키로 Set
	cache1.Set("user:1", "new-value")
	time.Sleep(100 * time.Millisecond) // ristretto 비동기 처리 대기

	// 현재 상황에서는 cache2 에 키가 남아있어야 함
	value, exists := cache2.Get("user:1")
	fmt.Printf("cache2 Get before invalidation: %v, exists: %v\n", value, exists)

	// cache1 에서 무효화 전파
	if err := cache1.Invalidate(ctx, "user:1"); err != nil {
		log.Printf("cach1 invalidate error: %v", err)
	}
	time.Sleep(100 * time.Millisecond) // ristretto 비동기 처리, pub/sub 대기

	// cache2에서 해당 키가 삭제되었는지 확인
	value, exists = cache2.Get("user:1")
	fmt.Printf("cache2 Get after invalidation: %v, exists: %v\n", value, exists)

	// cache1은 자신이 Set 했으므로 값이 있어야 함
	value, exists = cache1.Get("user:1")
	fmt.Printf("cache1 Get (should have value): %v, exists: %v\n", value, exists)

	fmt.Println("\n=== Test 2: Delete propagation ===")

	// cache2 에 동일한 키로 다시 저장
	cache2.Set("user:1", "new-value")
	time.Sleep(100 * time.Millisecond)

	// cache1 에서 Delete
	cache1.Delete("user:1")
	time.Sleep(100 * time.Millisecond)

	// 현재 상황에서는 cache2 에 키가 남아있어야 함
	value, exists = cache2.Get("user:1")
	fmt.Printf("cache2 Get before invalidation: %v, exists: %v\n", value, exists)

	// cache1 에서 무효화 전파
	if err := cache1.Invalidate(ctx, "user:1"); err != nil {
		log.Printf("cache1 delete error: %v", err)
	}
	time.Sleep(100 * time.Millisecond)

	value, exists = cache2.Get("user:1")
	fmt.Printf("cache2 Get after invalidation: %v, exists: %v\n", value, exists)

	value, exists = cache1.Get("user:1")
	fmt.Printf("cache1 Get after delete: %v, exists: %v\n", value, exists)

	fmt.Println("\n=== Done ===")
}
