# Story 2.2: Default Text-to-Speech Generation

Status: ready-for-dev

## 1. Story

**As a** user,
**I want** the system to automatically generate Text-to-Speech (TTS) from the generated script using Eleven Labs,
**so that** I have a voiceover for my video without needing to record it myself.

## 2. Acceptance Criteria

1.  **Given** a script has been generated (from Story 2.1),
    **When** the TTS generation process is initiated,
    **Then** an audio file is successfully created containing the voiceover for the script.
2.  **Given** the audio file is generated,
    **When** it is played back,
    **Then** the audio quality is clear and suitable for use in a professional video.
3.  **Given** the TTS process requires the Eleven Labs API,
    **When** the system connects to the API,
    **Then** it successfully authenticates using the `ELEVEN_API_KEY` from an environment variable.
4.  **Given** the TTS generation is in progress,
    **When** the process is active,
    **Then** the user sees a progress indicator in the terminal (e.g., "Generating voiceover...").

## 3. Developer Context

### Previous Story Intelligence (Learnings from Story 2.1)
-   The application's entry point and main logic flow are in `eleven_video/main.py`. New functionality should be integrated there.
-   API keys are managed via environment variables. This pattern must be continued for the `ELEVEN_API_KEY`.
-   Terminal-based user feedback (e.g., progress messages) is a core requirement.
-   Unit tests with mocked API calls are the standard for testing new services.

### Technical Requirements
-   **Primary Goal:** Implement a `generate_tts` function that takes a script string as input and saves the generated audio to a file.
-   **API Integration:** This function must integrate with the Eleven Labs API for TTS.
-   **Authentication:** API calls must be authenticated using an API key stored in the `ELEVEN_API_KEY` environment variable.
-   **Error Handling:** Implement robust error handling for API calls, including connection errors, authentication failures, and usage limit errors.
-   **User Feedback:** Provide clear feedback to the user in the terminal, including a "Generating voiceover..." message and a success or failure notification with the output file path.
-   **Output:** The generated audio should be saved to a predictable location, such as a temporary or output directory.

### Architectural Compliance
-   **Modularity:** The TTS generation logic should be encapsulated within its own function in `eleven_video/main.py`. As the project grows, consider moving it to a dedicated `eleven_video/audio_generator.py`.
-   **Dependencies:** The function will depend on the output of the script generation from Story 2.1. The main application flow will orchestrate passing the script to this new function.
-   **Configuration:** The application must read the `ELEVEN_API_KEY` from environment variables.

### Library & Framework Requirements
-   **HTTP Client/SDK:** Use the official `elevenlabs` Python SDK for interacting with the API. This should be preferred over a manual `requests` implementation.
-   **Dependencies:** Add `elevenlabs` to the `requirements.txt` file.

### File & Code Structure
-   `eleven_video/main.py`: Add the `generate_tts` function here and integrate it into the main video creation pipeline.
-   `requirements.txt`: Add `elevenlabs` to this file.
-   `.env.example`: Add `ELEVEN_API_KEY=""` to this file.

### Testing Requirements
-   **Unit Tests:** Create unit tests for the `generate_tts` function.
    -   Mock the Eleven Labs API client to test the function's behavior without making actual API calls.
    -   Test successful audio file creation.
    -   Test various API error scenarios.

### Git Intelligence
-   Follow standard commit message conventions: `feat(audio): Add Eleven Labs TTS generation`.

### Project Context Reference
-   This story directly implements a core feature described in the PRD.
-   **Source:** `docs/prd.md` (FR6, FR35)
-   **Source:** `docs/epics.md` (Epic 2, Story 2.2)
-   **Source:** `docs/sprint-artifacts/story-2-1-default-script-generation-from-prompt.md` (for implementation patterns)

## 4. Completion Status
**Status:** ready-for-dev
**Completion Notes:**
-   Ultimate context engine analysis completed - comprehensive developer guide created.
-   This story builds on the script generation functionality and is a critical step in the core video pipeline.
