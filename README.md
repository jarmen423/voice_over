After script is done to add new audio file to your video run:
```bash
ffmpeg -i <video>.mp4 -i <promo_video_subtitles_FINAL_TAGGED>.mp3 -c:v copy -map 0:v -map 1:a -shortest final_video.mp4
```