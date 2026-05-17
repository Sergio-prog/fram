# CLI

Strict commands are no-input and scriptable:

```bash
fram resize input.jpg 128x128 -o output.jpg
fram crop input.jpg 128x128 --anchor center -o output.jpg
fram convert input.png webp -o output.webp
fram rotate input.jpg 90 -o rotated.jpg
fram flip input.jpg --horizontal -o flipped.jpg
fram cut input.mp4 --start 5 --duration 10 -o output.mp4
fram strip-audio input.mp4 -o silent.mp4
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

Video cut slider:

```text
Tab         switch start/end edge
Left/Right  move the active edge
```

The slider writes the generated `start end` range into the params input when video duration can be read with `ffprobe`.

Preview notes:

- image files are shown directly
- video files render a temporary preview frame with FFmpeg
- unsupported terminals may fall back inside `textual-image`
