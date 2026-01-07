# Nano Banana - Image Generation Skill

Generate images from text prompts via eng0's data API using Google Nano Banana (Gemini).

## Models

| Model | Resolution | Best For |
|-------|------------|----------|
| `flash` | 1024px | Fast, high-volume |
| `pro` | Up to 4K | Professional quality |

## Quick Examples

### Generate Image (Flash)
```bash
curl -X POST https://api.eng0.ai/api/data/images/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A sunset over mountains", "aspectRatio": "16:9"}'
```

### Generate 4K Image (Pro)
```bash
curl -X POST https://api.eng0.ai/api/data/images/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Product photo on white background", "model": "pro", "imageSize": "4K"}'
```

## Aspect Ratios

`1:1`, `16:9`, `9:16`, `4:3`, `3:4`, `21:9`, `2:3`, `3:2`, `4:5`, `5:4`

## Response

```json
{
  "image": {
    "base64": "...",
    "mimeType": "image/png",
    "dataUrl": "data:image/png;base64,..."
  },
  "description": "..."
}
```

## Complements

- **deep-research** - Generate illustrations for reports
- **market-data** - Stock data for financial visualizations
