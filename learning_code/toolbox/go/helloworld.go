package main

import "fmt"
import "test/fm"


func main(){
	var v1 = 1
	var v2 = 1
	var v3 bool = false
	var v4 string = "Hello World!"
	v5 := true
	fmt.Println(v1)
	fmt.Println(add(v1,v2))
	fmt.Println(v3)
	fmt.Println(v4)
	fmt.Println(v5)
	fm.Pr()
}

func add(a int,b int) int{
	return a+b
}