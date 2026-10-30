package fm

import "fmt"

type usr struct{
	Name string
	Age int

}

func Pr(){
	u := usr{
		Age: 18,
		Name: "Asuna",
	}
	fmt.Println(u.Name)
	fmt.Println(u.Age)
}