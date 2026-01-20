package main

import (
	"context"
	"fmt"
	"time"
)

func case2A() {
	go func() {
		for {
			fmt.Println("[goroutine1] working...")
			time.Sleep(1 * time.Second)
		}
	}()

	go func() {
		for i := 0; i < 5; i++ {
			fmt.Println("[goroutine2] working...")
		}
	}()

	time.Sleep(5 * time.Second)
	fmt.Println("[main] exit")
}

func case2B() {
	ctx, cancel := context.WithCancel(context.Background())

	go func(ctx context.Context) {
		for {
			select {
			case <-ctx.Done():
				fmt.Println("[goroutine1] cancelled:", ctx.Err())
				return
			default:
				fmt.Println("[goroutine1] working...")
				time.Sleep(1 * time.Second)
			}
		}
	}(ctx)

	time.Sleep(3 * time.Second)
	fmt.Println("[main] cancel context")
	cancel()

	time.Sleep(1 * time.Second)
	fmt.Println("[main] exit")
}
