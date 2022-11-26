package main

import (
	"fmt"
	ffmpeg "github.com/u2takey/ffmpeg-go"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"encoding/json"
)

func main() {
	// if no args, print usage
	usage := "Usage: 8mb <file> [multiplier]\n\tfile: path to file to shrink\n\tmultiplier: optional, default 8.0, the multiplier to the size/duration of the file"
	if len(os.Args) < 2 {
		fmt.Println(usage)
		os.Exit(1)
	}
	// if -h, -help, --help or /? print usage)
	if os.Args[1] == "-h" || os.Args[1] == "-help" || os.Args[1] == "--help" || os.Args[1] == "/?" {
		fmt.Println(usage)
		os.Exit(1)
	}
	file := os.Args[1]
	size := 8192.0
	multiplier := 8.0
	// if there is a second argument, use it as the multiplier
	if len(os.Args) > 2 {
		multiplier, _ = strconv.ParseFloat(os.Args[2], 64)
	}
	size = size * multiplier
	shrinkFile(file, size)
}

func shrinkFile(file string, size float64) {
	output := strings.TrimSuffix(file, filepath.Ext(file)) + ".shrunk.mp4"
	duration := getDuration(file)
	bitrate := int(size / duration)
	fmt.Printf("Shrinking %s to %.2fKB. Bitrate: %dk\n", file, size, bitrate)
	if err := ffmpeg.
		Input(file).Output(output, ffmpeg.KwArgs{"b": fmt.Sprintf("%dk", bitrate), "filter:v": "fps=24", "c:a": "copy", "pix_fmt": "yuv420p10le", "c:v": "libx264"}).
		Run(); err != nil {
		fmt.Println(err)
	}
	fmt.Printf("Shrunk to %s\n", shrinkPercentage(file, output))
}

type Probe struct {
	Format struct {
		Duration string `json:"duration"`
	} `json:"format"`
}

func getDuration(file string) float64 {
	data, err := ffmpeg.Probe(file, ffmpeg.KwArgs{})
	if err != nil {
		fmt.Println(err)
	}
	probe := Probe{}
	if err := json.Unmarshal([]byte(data), &probe); err != nil {
		fmt.Println(err)
	}
	duration, _ := strconv.ParseFloat(probe.Format.Duration, 64)
	return duration
}

func shrinkPercentage(file, output string) string {
	fi, _ := os.Stat(file)
	fo, _ := os.Stat(output)
	return fmt.Sprintf("%.2f%%", float64(fo.Size())/float64(fi.Size())*100)
}