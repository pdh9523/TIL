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
	if err := cache2.Set(ctx, "user:1", "old-value"); err != nil {
		log.Printf("cache2 set error: %v", err)
	}
	time.Sleep(100 * time.Millisecond) // ristretto 비동기 처리 대기

	// cache2 에서 해당 키 조회시 조회 가능
	value, exists := cache2.Get("user:1")
	fmt.Printf("cache2 Get before invalidation: %v, exists: %v\n", value, exists)

	// cache1에서 같은 키로 Set → cache2에 invalidation 전파
	if err := cache1.Set(ctx, "user:1", "new-value"); err != nil {
		log.Printf("cache1 set error: %v", err)
	}
	time.Sleep(100 * time.Millisecond) // Pub/Sub 전파 대기

	// cache2에서 해당 키가 삭제되었는지 확인
	value, exists = cache2.Get("user:1")
	fmt.Printf("cache2 Get after invalidation: %v, exists: %v\n", value, exists)

	// cache1은 자신이 Set 했으므로 값이 있어야 함
	value, exists = cache1.Get("user:1")
	fmt.Printf("cache1 Get (should have value): %v, exists: %v\n", value, exists)

	fmt.Println("\n=== Test 2: Delete propagation ===")

	// cache1에서 Delete
	if err := cache1.Delete(ctx, "user:1"); err != nil {
		log.Printf("cache1 delete error: %v", err)
	}

	time.Sleep(100 * time.Millisecond)

	value, exists = cache1.Get("user:1")
	fmt.Printf("cache1 Get after delete: %v, exists: %v\n", value, exists)

	fmt.Println("\n=== Done ===")
}
