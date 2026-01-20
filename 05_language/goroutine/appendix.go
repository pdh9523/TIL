package main

import (
	"fmt"
	"runtime"
	"sync"
	"time"
)

func cpuBound() {
	var x uint64
	for i := 0; i < 1e9; i++ {
		x += uint64(i)
	}
}

func worker(id int, wg *sync.WaitGroup) {
	defer wg.Done()

	fmt.Printf("worker id: %d start ...\n", id)
	cpuBound()
	fmt.Printf("worker id: %d end ...\n", id)
}

func appendix() {
	now := time.Now()
	fmt.Printf("CPU COUNTS: %d \n", runtime.NumCPU())

	runtime.GOMAXPROCS(1)

	fmt.Printf("GOMAXPROCS: %d \n", runtime.GOMAXPROCS(0))

	var wg sync.WaitGroup
	numWorkers := 5

	for i := 1; i <= numWorkers; i++ {
		wg.Add(1)
		go worker(i, &wg)
	}

	wg.Wait()

	fmt.Printf("Total: %fs", time.Since(now).Seconds())
}
