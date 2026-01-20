package main

import (
	"fmt"
	"time"
)

func case1A() {
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

func case1B() {
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
