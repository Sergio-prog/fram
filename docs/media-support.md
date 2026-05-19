# Media Support

Images:

```text
resize
crop
compress
convert
rotate
flip
strip-metadata
blur
grayscale
```

Videos:

```text
cut
resize
crop
fps
compress
convert
strip-audio
strip-metadata
extract-audio
extract-frame
blur
grayscale
gif
speed
reverse
```

SVG is intentionally not treated as normal raster input. Add `cairosvg` later if SVG-to-raster conversion is needed.

Video work depends on local FFmpeg availability and codecs.
