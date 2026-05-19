# API

FastAPI entry point:

```bash
uvicorn fram.api.main:app --reload
```

Routes:

```text
GET  /health
POST /media/info
POST /media/process
POST /images/process
POST /videos/process
```

Auth:

- disabled when `FRAM_API_TOKEN` is empty
- enabled when `FRAM_API_TOKEN` is set
- header: `Authorization: Bearer <token>`

`/media/process` accepts multipart form data:

- `file`: uploaded media
- `operations`: JSON array
- `output_suffix`: optional suffix like `.webp` or `.mp4`

Operation names accepted by the API:

```text
resize
crop
compress-image
compress-video
convert
rotate
flip
strip-metadata
blur
grayscale
cut
fps
strip-audio
extract-audio
extract-frame
gif
speed
reverse
```
