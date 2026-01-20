package main

import (
	"fmt"
	"time"
)

func case1() {
	defer func() {
		if r := recover(); r != nil {
			fmt.Println("[main] recovered:", r)
		}
	}()

	go func() {
		defer func() {
			if r := recover(); r != nil {
				fmt.Println("[goroutine] recovered:", r)
			}
		}()

		fmt.Println("[goroutine] start panic")
		panic("panic in goroutine")
	}()

	time.Sleep(1 * time.Second)
	fmt.Println("[main] finished")
}

func case1_4() {
	defer func() {
		if r := recover(); r != nil {
			fmt.Println("[main] recovered:", r)
		}
	}()

	go func() {
		fmt.Println("[goroutine] start panic")
		panic("panic in goroutine")
	}()

	time.Sleep(1 * time.Second)
	fmt.Println("[main] finished")
}
