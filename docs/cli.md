# CLI

Strict commands are no-input and scriptable:

```bash
fram resize input.jpg 128x128 -o output.jpg
fram crop input.jpg 128x128 --anchor center -o output.jpg
fram convert input.png webp -o output.webp
fram rotate input.jpg 90 -o rotated.jpg
fram flip input.jpg --horizontal -o flipped.jpg
fram strip-metadata input.jpg -o clean.jpg
fram blur input.jpg --radius 2 -o blurred.jpg
fram grayscale input.jpg -o gray.jpg
fram adjust input.jpg --brightness 1.1 --contrast 1.2 -o adjusted.jpg
fram sharpen input.jpg --factor 2 -o sharp.jpg
fram watermark input.jpg "FRAM" -o watermarked.png
fram upscale input.jpg --factor 2 -o large.jpg
fram auto-orient input.jpg -o oriented.jpg
fram background transparent.png white -o flattened.jpg
fram cut input.mp4 --start 5 --duration 10 -o output.mp4
fram rotate input.mp4 90 -o rotated.mp4
fram flip input.mp4 --horizontal -o flipped.mp4
fram grayscale input.mp4 -o gray.mp4
fram strip-audio input.mp4 -o silent.mp4
fram mute-audio input.mp4 -o muted.mp4
fram extract-audio input.mp4 -o audio.m4a
fram extract-frame input.mp4 --at 00:00:05 -o frame.png
fram thumbnail input.mp4 --at 00:00:05 -o thumbnail.png
fram contact-sheet input.mp4 --columns 3 --rows 3 -o sheet.png
fram extract-subtitles input.mp4 -o subtitles.srt
fram gif input.mp4 --fps 12 --width 480 -o clip.gif
fram speed input.mp4 2 -o fast.mp4
fram reverse input.mp4 -o reversed.mp4
```

Help:

```bash
fram --help
fram resize --help
fram help resize
```

Interactive commands:

```bash
fram
fram input.jpg
fram input.mp4
```

Interactive mode stays compact by default and reveals details with `i`. It renders real terminal image previews through `textual-image` when the terminal supports image protocols.

Current TUI flow:

```text
select file -> select action -> enter params -> add operation -> run
```

TUI sliders:

```text
Tab         switch active slider
Left/Right  adjust active slider
```

The cut slider writes the generated `start end` range into the params input when video duration can be read with `ffprobe`. Numeric sliders are available for actions like `adjust`, `compress`, `blur`, `fps`, `gif`, and `speed`.

Preview notes:

- image files are shown directly
- video files render a temporary preview frame with FFmpeg
- unsupported terminals may fall back inside `textual-image`
