---
stepsCompleted: [1, 2, 3, 4]
inputDocuments: ["docs/prd.md", "docs/architecture.md"]
---

# Eleven-labs-AI-Video - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for Eleven-labs-AI-Video, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements
FR1: Users can generate videos from text prompts through interactive terminal sessions
FR2: Users can specify custom voice models for text-to-speech generation
FR3: Users can select different image generation models for visual content
FR4: Users can customize the video output with pre-generation options
FR5: The system can automatically generate scripts from user prompts using AI
FR6: The system can create text-to-speech audio from generated scripts
FR7: The system can generate images that match the script content
FR8: The system can compile generated audio, images, and script into a final video
FR9: The system can apply professional video editing features during compilation
FR10: The system can apply subtle zoom effects to images during video compilation
FR11: Users can control image duration timing to 3-4 seconds per image
FR12: The system can automatically synchronize image timing with audio
FR13: The system can output videos in 16:9 aspect ratio optimized for YouTube
FR14: The system can export videos with professional pacing and timing
FR15: Users can interact with the system through an interactive terminal interface
FR16: Users can initiate video creation through an interactive terminal session
FR17: Users can select from available voice options through interactive prompts
FR18: Users can select from available image models through interactive prompts
FR19: Users can select from available Gemini text generation models through interactive prompts
FR20: Users can access help documentation within the interactive terminal
FR21: Users can configure settings through interactive configuration prompts
FR22: Users can check API status and usage through interactive status checks
FR23: Users can receive progress updates during video generation
FR24: Users can select video format, length, and other options through interactive prompts
FR24.1: Users can select Gemini text generation model as part of pre-generation configuration
FR25: Users can configure default settings that persist between sessions
FR25.1: Users can configure default Gemini text generation model preferences
FR26: The system can store user preferences in a configuration file
FR27: Users can manage multiple API key profiles
FR28: Users can set environment variables for API keys
FR29: The system can apply user preferences to video generation parameters
FR30: The system can output videos in MP4 format
FR31: The system can output videos in MOV format
FR32: The system can output videos in additional formats (AVI, WebM)
FR33: The system can maintain consistent video quality across output formats
FR34: Users can specify output resolution settings
FR35: The system can integrate with Eleven Labs API for TTS and sound effects
FR35.1: The system can integrate with Google Gemini Nano Banana (`gemini-2.5-flash-image`) for image generation
FR35.2: [FUTURE SCOPE] The system can integrate with Eleven Labs API for image generation (when API becomes available)
FR36: The system can integrate with Google Gemini API for script generation
FR36.1: The system can integrate with multiple Gemini text generation models
FR37: The system can provide real-time API usage monitoring during processing
FR37.1: The system can provide model-specific usage metrics for Google Gemini API
FR38: Users can view live consumption data during video generation
FR39: Users can see API quota information during processing
FR40: The system can track API costs during video generation
FR41: The system can maintain 80% success rate for complete video generation
FR42: The system can handle API rate limits gracefully with queuing
FR43: The system can provide fallback mechanisms when APIs are unavailable
FR44: The system can cache intermediate outputs to optimize API usage
FR45: The system can retry failed operations automatically
FR46: Users can generate multiple videos in batch mode
FR47: The system can process multiple video requests in sequence
FR48: The system can manage queueing for multiple video generation tasks
FR49: The system can operate in non-interactive mode for scripting
FR50: The system can provide standardized exit codes for automation
FR51: The system can support JSON output mode for parsing results in scripts
FR52: The system can support input/output redirection for integration with other tools

### NonFunctional Requirements
(Content unchanged)

### FR Coverage Map

FR1: Epic 2
FR2: Epic 3
FR3: Epic 3
FR4: Epic 3
FR5: Epic 2
FR6: Epic 2
FR7: Epic 2
FR8: Epic 2
FR9: Epic 2
FR10: Epic 2
FR11: Epic 2 (implemented in Story 2.4)
FR12: Epic 2 (implemented in Story 2.4)
FR13: Epic 2 (implemented in Story 2.4)
FR14: Epic 2 (implemented in Story 2.4)
FR15: Epic 1
FR16: Epic 1
FR16.1: Epic 3
FR17: Epic 3
FR18: Epic 3
FR19: Epic 3
FR20: Epic 1
FR21: Epic 1
FR22: Epic 1
FR23: Epic 2
FR24: Epic 3
FR24.1: Epic 3
FR25: Epic 1
FR25.1: Epic 3
FR25.2: Epic 3
FR25.3: Epic 3
FR25.4: Epic 3
FR26: Epic 1
FR27: Epic 1
FR28: Epic 1
FR29: Epic 1
FR30: Epic 2 (implemented in Story 2.4)
FR31: Future Scope
FR32: Future Scope
FR33: Future Scope
FR34: Epic 3
FR35: Epic 2
FR35.1: Epic 2
FR35.2: Future Scope (Post-MVP)
FR36: Epic 2
FR36.1: Epic 3
FR37: Epic 5
FR37.1: Epic 5
FR38: Epic 5
FR39: Epic 5
FR40: Epic 5
FR41: NFR (test acceptance criteria)
FR42: Epic 2 (implemented via tenacity retry)
FR43: Future Scope
FR44: Future Scope
FR45: Epic 2 (implemented via tenacity retry)
FR46: Future Scope
FR47: Future Scope
FR48: Future Scope
FR49: Future Scope
FR50: Epic 1
FR51: Epic 1
FR52: Future Scope

### Epic 1: Interactive Terminal Setup and Configuration
Users can install the tool, configure API keys, and set up their environment to generate videos locally.
**FRs covered:** FR15, FR16, FR20, FR21, FR22, FR25, FR26, FR27, FR28, FR29, FR50, FR51

### Epic 2: Core Video Generation Pipeline
Users can provide a text prompt and generate a complete video with script, voiceover, images, and compilation. **Includes video timing, aspect ratio, and professional output (absorbed from Epic 4).**
**FRs covered:** FR1, FR5, FR6, FR7, FR8, FR9, FR10, FR11, FR12, FR13, FR14, FR23, FR30, FR35, FR35.1, FR36, FR42, FR45

### Epic 3: Pre-generation Customization
Users can select specific voice models, image generation models, Gemini text generation models, and video duration before starting video generation. **Includes configurable defaults and `--interactive` flag.**
**FRs covered:** FR2, FR3, FR4, FR16.1, FR17, FR18, FR19, FR24, FR24.1, FR25.1, FR25.2, FR25.3, FR25.4, FR34, FR36.1

### ~~Epic 4: Video Processing and Timing Control~~ (DISSOLVED)
> **Note:** Epic 4 has been merged into Epic 2. Stories 4.1-4.4 were already implemented in Story 2.4. Story 4.5 (custom resolution) moved to Epic 3.

### Epic 5: Advanced API Monitoring
Users can monitor API usage, costs, and quotas in real-time during video generation.
**FRs covered:** FR37, FR37.1, FR38, FR39, FR40

### ~~Epic 6: Quality and Reliability Features~~ (DISSOLVED)
> **Note:** Epic 6 has been dissolved. FR41 (80% success rate) is a test metric, not an implementable story. FR42/FR45 (retry) already implemented via tenacity decorators in adapters. FR43/FR44 (fallback/caching) deferred to Future Scope.

### ~~Epic 7: Advanced Output and Batch Processing~~ (DISSOLVED)
> **Note:** Epic 7 has been dissolved. FR30 (MP4) implemented in Story 2.4. FR50/FR51 (exit codes, JSON) moved to Epic 1. Remaining features (batch mode, additional formats) deferred to Future Scope.

---
## Epic 1: Interactive Terminal Setup and Configuration

Users can install the tool, configure API keys securely, and set up their environment with local execution. Implements security-first API key management with .env support and ensures <10s startup time. **Addresses root need: Secure, fast setup that enables all future functionality**

### Story 1.1: Terminal Installation and Basic Execution
As a developer, I want to install the Eleven Labs AI Video tool via package manager, so that I can start using it from my terminal quickly.
**Acceptance Criteria:**
**Given** I have Python installed on my system, **When** I run the installation command, **Then** the tool is installed and available in my terminal, **And** I can execute the basic help command to see available options.

### Story 1.2: API Key Configuration via Environment Variables
As a user, I want to configure my Eleven Labs and Google Gemini API keys via environment variables, so that my keys are stored securely without being logged or displayed.
**Acceptance Criteria:**
**Given** I have valid API keys from Eleven Labs and Google Gemini, **When** I set the appropriate environment variables, **Then** the application can access the API keys securely, **And** the keys are never displayed in terminal history or logs.

### Story 1.3: Interactive Setup and Configuration File Creation
As a user, I want to run an interactive setup command that helps me configure default settings, so that I can persist my preferences between sessions without manual configuration.
**Acceptance Criteria:**
**Given** I have installed the application, **When** I run the interactive setup command, **Then** I am guided through configuration options, **And** a configuration file is created with my settings in my home directory.

### Story 1.4: Terminal Help System
As a user, I want to access comprehensive help documentation within the terminal, so that I can understand how to use the tool without leaving my workflow.
**Acceptance Criteria:**
**Given** I am using the terminal application, **When** I run the help command, **Then** I see clear documentation about available commands, **And** I can access context-specific help for each feature.

### Story 1.5: API Status and Usage Checking
As a user, I want to check API status and my current usage quotas from the terminal, so that I can verify my API keys are working before starting video generation.
**Acceptance Criteria:**
**Given** I have configured my API keys, **When** I run the API status command, **Then** I see the current status of my API connections, **And** I see my current usage quotas and limits.

### Story 1.6: Multiple API Key Profile Management
As a user, I want to manage multiple API key profiles for different projects or environments, so that I can switch between different API configurations easily.
**Acceptance Criteria:**
**Given** I have multiple sets of API keys, **When** I use the profile management commands, **Then** I can create, list, and switch between different API key profiles, **And** I can specify which profile to use for each operation.

---
## Epic 2: Core Video Generation Pipeline

Users can provide a simple text prompt and generate a complete video with script, voiceover, images, and compilation. **Includes video timing, aspect ratio, and professional output quality (absorbed from Epic 4).** **Addresses root need: Validation that the core dependency on external APIs works and delivers value.**

### Story 2.1: Default Script Generation from Prompt
As a user, I want the system to automatically generate a script from my text prompt using Google Gemini 2.5 Flash (`gemini-2.5-flash`, with option to switch models), so that I don't need to write a script manually.
**Acceptance Criteria:**
**Given** I have provided a text prompt, **When** the script generation process runs, **Then** a coherent script is generated based on my prompt using Gemini 2.5 Flash (`gemini-2.5-flash` or user-selected model), **And** the system successfully authenticates with the Google Gemini API.

### Story 2.2: Default Text-to-Speech Generation
As a user, I want the system to automatically generate TTS from the generated script using Eleven Labs, so that I have voiceover for my video without needing to record it.
**Acceptance Criteria:**
**Given** I have a generated script, **When** the TTS generation process runs, **Then** an audio file is created with voiceover of the script, **And** the audio quality is suitable for video use.

### Story 2.3: Default Image Generation from Script
As a user, I want the system to automatically generate matching images from the script using Google Gemini Nano Banana (`gemini-2.5-flash-image`), so that I have visual content for my video without needing to create images manually.
**Acceptance Criteria:**
**Given** I have a generated script, **When** the image generation process runs, **Then** images are generated based on thematic keywords extracted from the script sentences using Gemini Nano Banana (`gemini-2.5-flash-image`), **And** the images are of a consistent and appropriate style.

### Story 2.3.1: Image Generation Reliability & API Compliance
As a user, I want image generation to work reliably with correct API usage and handle errors gracefully, so that video generation succeeds consistently without cryptic API errors.

**Acceptance Criteria:**
1. **Given** the system calls the Gemini Image API, **When** `generate_content()` is called, **Then** `response_modalities=["IMAGE"]` config is included in the request.
2. **Given** a model ID is not specified, **When** selecting a default image model, **Then** the system queries available models dynamically and selects the first valid Gemini image model, with `gemini-2.5-flash-image` as hardcoded fallback.
3. **Given** the API returns an empty response (safety filter), **When** parsing the response, **Then** the system detects the empty response and raises a user-friendly error message instead of crashing with `NoneType` errors.
4. **Given** content is blocked by safety filters, **When** the first attempt fails, **Then** the system retries up to 2 times with a modified prompt (appending "safe for work, educational" suffix).
5. **Given** I am using the free tier, **When** generating images, **Then** the default model is `gemini-2.5-flash-image` (500/day free) to maximize free usage.

**Architecture Reference:** ADR-005 (Gemini Image Generation API Architecture)

**Tasks:**
- [ ] Task 1: Fix `_generate_image_with_retry()` to include `response_modalities=["IMAGE"]` config
- [ ] Task 2: Add defensive response parsing (check `response.candidates[0].content` before accessing `.parts`)
- [ ] Task 3: Implement dynamic model discovery fallback chain in `generate_images()`
- [ ] Task 4: Add retry-with-modified-prompt logic for safety filter blocks
- [ ] Task 5: Update `list_image_models()` to filter only models that support `generate_content()` (exclude Imagen)
- [ ] Task 6: Add unit tests for empty response handling and retry logic
- [ ] Task 7: Add integration test for end-to-end image generation

### Story 2.4: Video Compilation from Assets
As a user, I want the system to compile the generated script, audio, and images into a single video file, so that I have a complete video for my original prompt.
**Acceptance Criteria:**
**Given** I have generated script, audio, and images, **When** the video compilation process runs, **Then** a single video file is created combining all elements, **And** the audio and images are synchronized, **And** the output is 1920x1080 (16:9) MP4 with H.264/AAC codecs.

> [!NOTE]
> **Epic 4 Absorption:** Story 2.4 implements FR11 (image timing), FR12 (audio sync), FR13 (16:9), FR14 (professional pacing), and FR30 (MP4 output). These were originally planned for Epic 4 but are fundamental to video compilation.

### Story 2.5: Progress Updates During Video Generation
As a user, I want to receive progress updates during video generation, so that I can understand how long the process will take and its current status.
**Acceptance Criteria:**
**Given** I have initiated video generation, **When** the generation process is running, **Then** I receive clear, textual progress updates for each stage (script, audio, images, compilation).

### Story 2.6: Interactive Video Generation Command
As a user, I want to run an interactive command that guides me through video creation, so that I can generate videos end-to-end without needing to understand the underlying pipeline.
**Acceptance Criteria:**
**Given** I have configured my API keys, **When** I run `eleven-video generate`, **Then** I am prompted for my video topic/prompt, **And** the system orchestrates script generation, TTS, image generation, and video compilation, **And** I see progress updates throughout the process (using Story 2.5's progress display), **And** the final video file path is displayed upon completion.

> [!NOTE]
> **FR1 Implementation:** Story 2.6 implements FR1 (*"Users can generate videos from text prompts through interactive terminal sessions"*) by orchestrating Stories 2.1-2.5 into a unified interactive experience. This is the primary user-facing entry point for Epic 2.

### Story 2.7: Apply Subtle Zoom Effects
As a user, I want the system to apply subtle zoom effects to images during video compilation, so that the video appears dynamic and non-generic.
**Acceptance Criteria:**
**Given** I have images for my video, **When** the editing process applies zoom effects, **Then** subtle zoom-in and zoom-out effects are applied to each image, **And** the video appears more dynamic and visually engaging.


---
## Epic 3: Pre-generation Customization

Users can select specific voice models, image generation models, Gemini text generation models, and video duration before starting video generation. **Addresses root need: Enabling users to get personalized results that match their specific requirements.**

### Story 3.1: Custom Voice Model Selection
As a user, I want to specify custom voice models for text-to-speech generation, so that my video has the voice characteristics I prefer.
**Acceptance Criteria:**
**Given** I have access to multiple voice models, **When** I select a specific voice model for TTS, **Then** the generated audio uses my selected voice.

### Story 3.2: Custom Image Generation Model Selection
As a user, I want to select different image generation models for visual content, so that my video images match the style I want.
**Acceptance Criteria:**
**Given** I have access to multiple image generation models, **When** I select a specific image generation model, **Then** the generated images use the selected model.

### Story 3.3: Interactive Voice Selection Prompts
As a user, I want to select from available voice options through interactive prompts, so that I can easily choose the voice I want without remembering specific model names.
**Acceptance Criteria:**
**Given** I am in an interactive session, **When** prompted to select a voice, **Then** the tool displays a numbered list of available voice options, **And** my selection is used for generation.

### Story 3.4: Interactive Image Model Selection Prompts
As a user, I want to select from available image models through interactive prompts, so that I can easily choose the image style I want without remembering specific model names.
**Acceptance Criteria:**
**Given** I am in an interactive session, **When** prompted to select an image model, **Then** the tool displays a numbered list of available image models, **And** my selection is used for image generation.

### Story 3.5: Gemini Text Generation Model Selection
As a user, I want to select from available Gemini text generation models through interactive prompts, so that I can control the style and quality of the generated script.
**Acceptance Criteria:**
**Given** I have access to multiple Gemini models, **When** I select a specific Gemini model via an interactive prompt, **Then** the script generation uses my selected model.

### Story 3.6: Video Duration Selection
As a user, I want to select a target video duration through interactive prompts, so that I can control how long my generated video will be.
**Acceptance Criteria:**
**Given** I am setting up video generation, **When** I select a video duration option (e.g., 1, 3, 5 minutes), **Then** the system generates a script and assets appropriate for that duration.

### Story 3.7: Default Preference Configuration
As a user, I want to configure default preferences for voice, image model, Gemini model, and video duration, so that I don't need to select these options each time I generate a video.
**Acceptance Criteria:**
**Given** I have configured defaults via `eleven-video setup`, **When** I generate a video without the `--interactive` flag, **Then** the system uses my configured defaults silently. **And Given** I run `eleven-video generate -i`, **When** the `-i` or `--interactive` flag is provided, **Then** the system shows all interactive prompts regardless of configured defaults.

### Story 3.8: Custom Output Resolution Selection
As a user, I want to specify output resolution settings for my videos, so that I can match my video resolution to my specific requirements.
**Acceptance Criteria:**
**Given** I am configuring video output, **When** I select a specific resolution (e.g., '1080p', '720p'), **Then** the video is generated at the specified resolution.

> [!NOTE]
> Story 3.8 was moved from Epic 4 (Story 4.5) as it is a pre-generation customization option.

---
## Epic 5: Advanced API Monitoring

Users can monitor API usage, costs, and quotas in real-time during video generation. **Addresses root need: Cost transparency and usage awareness.**

### Story 5.1: Real-time API Usage Monitoring During Processing
As a user, I want to see real-time API usage monitoring during video generation, so that I can track my consumption as the video is being created.
**Acceptance Criteria:**
**Given** I am generating a video, **When** API calls are being made, **Then** I can see live usage data, **And** the monitoring updates at least every 5 seconds.

### Story 5.2: Model-specific Usage Metrics for Gemini API
As a user, I want to receive model-specific usage metrics for the Google Gemini API, so that I can understand how different models affect my usage.
**Acceptance Criteria:**
**Given** I am using multiple Gemini models, **When** I check API usage, **Then** I can see usage metrics broken down by specific models.

### Story 5.3: Live Consumption Data Viewing
As a user, I want to view live consumption data during video generation, so that I can understand my costs as they occur.
**Acceptance Criteria:**
**Given** I am in the middle of video generation, **When** I check consumption data, **Then** I see current consumption statistics for the active session.

### Story 5.4: API Quota Information Display
As a user, I want to see API quota information during processing, so that I know how much capacity I have remaining.
**Acceptance Criteria:**
**Given** I am using API services, **When** I run a status check command, **Then** I see current quota usage and remaining capacity.

### Story 5.5: API Cost Tracking During Generation
As a user, I want the system to track API costs during video generation, so that I can understand the financial impact as it occurs.
**Acceptance Criteria:**
**Given** I am generating a video using APIs, **When** the generation process runs, **Then** I can see running cost totals for the active session.

---
## ~~Epic 6: Quality and Reliability Features~~ (DISSOLVED)

> [!NOTE]
> **Epic 6 has been dissolved.** The functionality is either already implemented or deferred:
> - **FR41 (80% success rate):** This is a test metric, not an implementable story. Tracked via acceptance tests.
> - **FR42, FR45 (retry):** Already implemented via `tenacity` decorators in `gemini.py` and `elevenlabs.py`.
> - **FR43 (fallbacks), FR44 (caching):** Deferred to Future Scope as premature optimization.

---
## ~~Epic 7: Advanced Output and Batch Processing~~ (DISSOLVED)

> [!NOTE]
> **Epic 7 has been dissolved.** The functionality is either already implemented, moved, or deferred:
> - **FR30 (MP4 output):** Implemented in Story 2.4.
> - **FR50 (exit codes), FR51 (JSON output):** Moved to Epic 1 as CLI infrastructure.
> - **FR31-33 (additional formats), FR46-49 (batch mode):** Deferred to Future Scope.

---
## Future Scope (Post-MVP)

The following features are deferred for future development after MVP completion:

### Output Formats
- **FR31:** MOV video output format
- **FR32:** Additional video formats (AVI, WebM)
- **FR33:** Consistent quality across formats

### Batch Processing & Automation
- **FR46:** Multiple video generation in batch mode
- **FR47:** Sequential batch processing
- **FR48:** Queue management for batch tasks
- **FR49:** Non-interactive mode for scripting
- **FR52:** Input/output redirection for tool integration

### Advanced Reliability
- **FR43:** API fallback mechanisms
- **FR44:** API response caching for optimization

### External Integrations
- **FR35.2:** Eleven Labs API for image generation (when API becomes available)