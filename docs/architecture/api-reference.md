# API Reference for Epic 2

> **Action Item:** Verify API endpoints before implementing Stories 2-1, 2-2, 2-3

## ElevenLabs Text-to-Speech API

### Endpoint
```
POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}
```

### Authentication
| Header | Value |
|--------|-------|
| `xi-api-key` | `$ELEVENLABS_API_KEY` |

### Request Body
```json
{
  "text": "Text to convert to speech",
  "model_id": "eleven_multilingual_v2",
  "voice_settings": {
    "stability": 0.5,
    "similarity_boost": 0.5
  }
}
```

### Response
- **Content-Type:** `audio/mpeg` (default mp3_44100_128)
- **Formats:** mp3, pcm, ulaw (configurable via `output_format` query param)

### Key Parameters
| Parameter | Description |
|-----------|-------------|
| `voice_id` | Voice ID from `/v1/voices` endpoint |
| `model_id` | `eleven_multilingual_v2` (recommended) |
| `output_format` | `mp3_44100_128`, `mp3_22050_32`, `pcm_44100` |
| `optimize_streaming_latency` | 0-4 (0=default, 4=max optimization) |

---

## Google Gemini API

### Text Generation Endpoint
```
POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
```

### Streaming Endpoint
```
POST https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent
```

### Authentication
| Header | Value |
|--------|-------|
| `x-goog-api-key` | `$GEMINI_API_KEY` |
| `Content-Type` | `application/json` |

### Request Body (Text Generation)
```json
{
  "contents": [
    {
      "parts": [
        { "text": "Your prompt here" }
      ]
    }
  ]
}
```

### Response Structure
```json
{
  "candidates": [
    {
      "content": {
        "parts": [
          { "text": "Generated response text" }
        ]
      }
    }
  ]
}
```

### Recommended Models
| Model | Use Case |
|-------|----------|
| `gemini-2.5-flash` | Fast text generation (default) |
| `gemini-1.5-pro` | Complex reasoning tasks |
| `gemini-2.0-flash-exp` | Experimental multimodal |

---

## Image Generation (Imagen)

### Endpoint
```
POST https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:generateImages
```

### Request Body
```json
{
  "prompt": "Description of image to generate",
  "numberOfImages": 1,
  "aspectRatio": "1:1"
}
```

### Notes
- Imagen 3 requires paid tier access
- All generated images include SynthID watermark
- Aspect ratios: `1:1`, `16:9`, `9:16`, `4:3`, `3:4`

---

## Environment Variables (Canonical Names)

| Service | Variable | Official Source |
|---------|----------|-----------------|
| ElevenLabs | `ELEVENLABS_API_KEY` | [ElevenLabs Docs](https://elevenlabs.io/docs) |
| Google Gemini | `GEMINI_API_KEY` | [Google AI Docs](https://ai.google.dev) |

---

*Verified: 2025-12-14*
