# Architecture Decision Records

## Architect Persona 1: "Stability First"
*Focus: Reliability, maintainability, proven technology*

**Key Decision: Local vs Cloud Processing Architecture**
- **Option A**: Complete local execution as specified in PRD
  - *Pros*: No external SaaS dependencies, data privacy, predictable costs
  - *Cons*: Higher resource requirements on user's machine, complex setup, harder to scale
- **Option B**: Hybrid approach (local orchestration with cloud processing)
  - *Pros*: Better resource utilization, easier updates, handles rate limits better
  - *Cons*: Introduces external dependencies, potential privacy concerns
- **Recommendation**: Go with Option A as specified in PRD for consistency with requirements

## Architect Persona 2: "Performance Optimizer"
*Focus: Speed, efficiency, user experience*

**Key Decision: API Integration and Caching Strategy**
- **Option A**: Direct API calls with basic caching
  - *Pros*: Simple implementation, low memory usage
  - *Cons*: Prone to rate limits, slower response times during peak usage
- **Option B**: Intelligent caching with queue management
  - *Pros*: Better rate limit handling, improved user experience, cost optimization
  - *Cons*: More complex implementation, higher memory requirements
- **Recommendation**: Option B to meet the 80% success rate requirement and handle API rate limits gracefully

## Architect Persona 2: "Security Guardian"
*Focus: Security, privacy, compliance*

**Key Decision: Configuration and Credential Management**
- **Option A**: JSON config file with encrypted API keys
  - *Pros*: Simple to implement, standard approach
  - *Cons*: Encryption adds complexity, potential for user error
- **Option B**: Environment variables with OS-level credential storage
  - *Pros*: Better security practices, leverages OS security features
  - *Cons*: More complex setup for users, platform-specific implementation
- **Recommendation**: Hybrid approach using environment variables as primary with JSON config as fallback

## Architect Persona 3: "Scalability Master"
*Focus: Future growth, extensibility, modularity*

**Key Decision: Component Architecture Pattern**
- **Option A**: Monolithic terminal application
  - *Pros*: Simpler to develop and deploy, easier debugging
  - *Cons*: Harder to maintain as features grow, difficult to test individual components
- **Option B**: Modular micro-components with clear interfaces
  - *Pros*: Better maintainability, easier testing, extensibility for future features
  - *Cons*: More complex initial architecture, potential performance overhead
- **Recommendation**: Modular approach with clear separation of concerns but implemented within a single executable

## Cross-Cutting Architectural Decision: Error Handling and Resilience
- **Option A**: Simple try-catch with basic retry
  - *Pros*: Minimal complexity
  - *Cons*: Poor user experience during API failures
- **Option B**: Comprehensive fallback strategies with graceful degradation
  - *Pros*: Robust user experience, handles API unavailability gracefully
  - *Cons*: Complex implementation
- **Recommendation**: Option B to meet the 80% success rate requirement and provide professional user experience

---

## ADR-005: Gemini Image Generation API Architecture

**Date**: 2026-01-05  
**Status**: Accepted  
**Context**: Investigation revealed fundamental architectural differences between Google's image generation APIs that were not properly addressed in the original implementation.

### Problem Statement

The original image generation implementation had multiple issues:
1. Hardcoded model IDs that didn't exist or were deprecated
2. Using `generateContent` for all image models (only works for Gemini, not Imagen)
3. No handling for empty responses (safety filter blocks)
4. No retry logic when content is filtered

### Decision

#### 1. Model Categories and API Methods

| Model Type | Example Model IDs | API Method | Config Required |
|------------|-------------------|------------|-----------------|
| **Gemini Image** | `gemini-2.5-flash-image` | `generate_content()` | `response_modalities=["IMAGE"]` |
| **Imagen** | `imagen-4.0-generate-001` | `generate_images()` | Different SDK pattern |

**Decision**: Use Gemini Image models (`gemini-2.5-flash-image`) as primary, since they work with `generate_content()` and have generous free tier (500/day).

#### 2. Model ID Resolution

**Problem**: Model IDs change frequently (models deprecated, renamed, or region-restricted).

**Decision**: 
- Query available models dynamically via `list_image_models()`
- Use first available Gemini image model as default
- Fall back to hardcoded known-working model if query fails

```python
# Priority order for default model selection:
1. User-specified via CLI flag (-m)
2. User's configured default (from setup)
3. First model from dynamic list_image_models() query
4. Hardcoded fallback: "gemini-2.5-flash-image"
```

#### 3. Response Handling

**Problem**: API can return empty responses when safety filters block content.

**Decision**: Implement defensive response parsing:
```python
# Check for valid response before accessing parts
if response.candidates and response.candidates[0].content:
    parts = response.candidates[0].content.parts
    # Parse image data...
else:
    # Handle empty response (safety filter, etc.)
    raise GeminiAPIError("Image generation blocked or empty response")
```

#### 4. Retry Strategy for Blocked Content

**Decision**: When safety filter blocks an image:
1. Retry with modified prompt (append "safe for work, educational" suffix)
2. Maximum 2 retries before failing
3. Log warning about which prompts were filtered

#### 5. Free Tier Optimization

| Model | Free Tier | Paid Cost |
|-------|-----------|-----------|
| Gemini 2.5 Flash Image | **500/day** | $0.039/image |
| Imagen 4 Fast | 100/day | $0.02/image |
| Imagen 4 Standard | 10-50/day | $0.04/image |

**Decision**: Default to Gemini 2.5 Flash Image for best free tier allowance.

### Consequences

**Positive**:
- Reliable image generation with proper API usage
- Dynamic model discovery prevents deprecated model issues
- Graceful handling of safety filter blocks
- Optimized for free tier users

**Negative**:
- Imagen models not supported without additional implementation
- Requires network call to discover models (cached for performance)

### Implementation Files

- `eleven_video/api/gemini.py` - GeminiAdapter class
- `eleven_video/ui/image_model_selector.py` - Model selection UI
- `eleven_video/main.py` - CLI integration

