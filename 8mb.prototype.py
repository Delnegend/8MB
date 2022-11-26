# #/bin/bash
# #set -o xtrace
# targetSizeKilobytes=8192
# fileInput=$1
# ext="${fileInput##*.}"; 
# fileOutput="${fileInput}.shrunk.${ext}"
# durationSeconds=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $fileInput)
# bitrate=$(echo "scale=0; $targetSizeKilobytes/ $durationSeconds" | bc)
# #bitrate=$(($targetSizeKilobytes / $durationSeconds))
# beforeSizeBytes=$(stat --printf="%s" $fileInput)
# echo "Shrinking ${fileInput} to ${targetSizeKilobytes}KB. Bitrate: ${bitrate}k"
# ffmpeg \
# 	-y \
# 	-hide_banner \
# 	-loglevel error \
# 	-i "$fileInput" \
# 	-b ${bitrate}k \
# 	$fileOutput
# afterSizeBytes=$(stat --printf="%s" $fileOutput)
# shrinkPercentage=$(($beforeSizeBytes / $afterSizeBytes))
# echo "Rebuilt file as ${fileOutput}, shrank to ${shrinkPercentage}% of original size"


import subprocess as sp
import os
import sys

def shrink_file(file_input: str, target_size_kilobytes: int) -> None:
    file_output = os.path.splitext(file_input)[0] + '.shrunk.mp4'
    duration_seconds = float(sp.check_output([
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        file_input
    ]))
    bitrate = int(target_size_kilobytes / duration_seconds) * 8
    print(f'Shrinking {file_input} to {target_size_kilobytes}KB. Bitrate: {bitrate}k')
    sp.run([
        'ffmpeg',
        '-y',
        '-hide_banner',
        '-loglevel', 'error',
        '-i', file_input,
        '-b', f'{bitrate}k',
        '-filter:v', 'fps=24',
        '-c:a', 'copy',
        '-pix_fmt', 'yuv420p10le',
        '-c:v', 'libx264',
        file_output
    ])
    print(f'Built to {shrink_percentage(file_input, file_output)}')

def shrink_percentage(file_input: str, file_output: str) -> str:
    if not os.path.exists(file_output) or not os.path.exists(file_input):
        return 0
    if os.path.getsize(file_input) == 0:
        return 0
    return f"{os.path.getsize(file_output) / os.path.getsize(file_input) * 100:.2f}"

if __name__ == '__main__':
    shrink_file(sys.argv[1], 8192)