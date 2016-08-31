package main

import (
    "fmt"
    "github.com/paulmach/go.geo"
    "github.com/warrenwyf/go-geos/geos"
)


func main() {
    fmt.Printf("hello world\n")
    line, _ := geos.FromWKT("LINESTRING (0 0, 10 10, 20 20)")
    buf, _ := line.Buffer(2.5)
    fmt.Println(buf)

    p := geo.NewPoint(0, 0)
    p.SetX(10).Add(geo.NewPoint(10, 10))
    p.Equals(geo.NewPoint(20, 10))  // == true
}
