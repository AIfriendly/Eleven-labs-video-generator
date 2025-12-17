# Core Architectural Decisions

## Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- Data Architecture: JSON files in user's home directory for configuration
- Authentication & Security: Environment variables via .env files for API key management
- API & Communication: Circuit breaker pattern + retry with exponential backoff + queue management for API integration
- Testing Strategy: Comprehensive test coverage with unit (40%), integration (30%), and E2E (30%) tests to ensure reliability and maintainability

**Important Decisions (Shape Architecture):**
- Local execution without external SaaS dependencies
- CLI/Interactive Terminal Application using Python
- Real-time monitoring using Rich library for terminal displays
- Rate limiting and queue management with circuit breaker pattern
- Hexagonal (Ports and Adapters) architecture with clear separation of concerns
- Smart caching strategies to reduce API calls and improve performance
- Testable architecture with modular design enabling comprehensive unit and integration testing

**Deferred Decisions (Post-MVP):**
- OS-specific credential storage (Windows Credential Manager, macOS Keychain, Linux Secret Service) as enhancement

## Architecture Decision Records - Multi-Perspective Analysis

### Architect Persona 1: "Reliability First" (Focus: Stability & Production Readiness)
**Proposal for API Integration:**
- Decision: Circuit breaker pattern + retry with exponential backoff + queue management
- Technology: HTTPX with custom API adapter layer
- Rationale: The 80% success rate requirement is critical and must be achieved through robust error handling
- Trade-offs: High reliability but more complex implementation with potential latency from queuing

### Architect Persona 2: "Security Guardian" (Focus: Security & Privacy)
**Proposal for API Key Management:**
- Decision: Environment variables via .env files as the primary approach
- Additional: File permission checks (600 for .env files), secure credential handling
- Rationale: Protects user's API keys while maintaining ease of use
- Trade-offs: More secure but more complex setup for users with need for proper error handling

### Architect Persona 3: "Performance Optimizer" (Focus: Speed & Efficiency)
**Proposal for Data Architecture:**
- Decision: Minimal JSON config for settings, in-memory caching for API responses
- Additional: Smart caching strategies to reduce API calls and improve performance
- Rationale: Achieves <10 second startup time and <5 minute processing time
- Trade-offs: Fast startup times but memory usage considerations and cache invalidation complexity

### Architect Persona 4: "Developer Experience" (Focus: Maintainability & Simplicity)
**Proposal for Terminal Interface:**
- Decision: Typer for CLI + Rich for advanced terminal UI
- Additional: Consistent prompt patterns, comprehensive error messaging
- Rationale: Creates intuitive user experience as required in PRD
- Trade-offs: Excellent developer experience but additional dependencies and learning curve for team

### Architect Persona 5: "Scalability Master" (Focus: Future Growth & Extensibility)
**Proposal for Architecture Pattern:**
- Decision: Hexagonal (Ports and Adapters) architecture with clear separation of concerns
- Additional: Plugin architecture ready for additional AI services
- Rationale: Enables future growth and maintains flexibility
- Trade-offs: Highly maintainable but initial complexity, potentially over-engineered for MVP

### Consensus Decisions:
1. **API Integration:** Circuit breaker + queue management (Reliability First wins)
2. **Security:** Environment variables + encrypted config (Security Guardian wins)
3. **Performance:** Smart caching + minimal config (Performance Optimizer wins)
4. **Interface:** Typer + Rich (Developer Experience wins)
5. **Architecture:** Hexagonal with clear boundaries (Scalability Master wins)

## Data Architecture

**Configuration and State Storage:**
- Decision: JSON files in OS-standard user config directory via `platformdirs.user_config_dir("eleven-video")`
  - Windows: `%LOCALAPPDATA%\eleven-video\config.json`
  - Linux: `~/.config/eleven-video/config.json` (XDG-compliant)
  - macOS: `~/Library/Application Support/eleven-video/config.json`
- Rationale: Simple, accessible, and follows OS conventions for storing user preferences and non-sensitive configuration
- Affects: Configuration management, user experience consistency

## Authentication & Security

**API Key Management:**
- Decision: Environment variables via .env files as primary storage mechanism
- Rationale: Following security best practices while maintaining ease of use
- Security: API keys stored in .env files with appropriate file permissions (readable by owner only)
- Affects: Security, user setup experience, deployment

**Canonical Environment Variable Names:**
| Service | Variable | Auth Header | Official Source |
|---------|----------|-------------|-----------------|
| ElevenLabs | `ELEVENLABS_API_KEY` | `xi-api-key` | [ElevenLabs Docs](https://elevenlabs.io/docs) |
| Google Gemini | `GEMINI_API_KEY` | `x-goog-api-key` | [Google AI Docs](https://ai.google.dev) |

> ⚠️ **Important:** Always use the canonical names listed above. Do NOT use variations like `ELEVEN_API_KEY` or `GOOGLE_API_KEY`.

## API & Communication Patterns

**API Integration Architecture:**
- Decision: Circuit breaker pattern + retry with exponential backoff + queue management via API adapter layer
- Technology: HTTPX for both sync and async API calls
- Rationale: Required to meet 80% success rate with rate limit handling as specified in PRD
- Implementation: Custom API adapter layer to abstract Eleven Labs and Google Gemini APIs
- Affects: Reliability, performance, error handling

## Frontend Architecture

**Terminal User Interface:**
- Decision: Rich library for advanced terminal UI with Typer for CLI framework
- Rationale: Provides professional terminal experience with progress bars, tables, and real-time updates
- Affects: User experience, real-time monitoring capabilities

## Infrastructure & Deployment

**Local Application Architecture:**
- Decision: Single Python executable with Poetry for dependency management using Hexagonal (Ports and Adapters) architecture
- Rationale: Supports local execution requirement with cross-platform compatibility while enabling testability and maintainability
- Affects: Distribution, installation, performance, future extensibility

## Decision Impact Analysis

**Implementation Sequence:**
1. API adapter layer with circuit breaker and queue management (foundational)
2. Configuration management with secure credential handling
3. Terminal UI with Rich library integration
4. Real-time monitoring and progress tracking
5. Video pipeline orchestration
6. Caching layer implementation

**Cross-Component Dependencies:**
- API adapter layer required by all API interaction components
- Configuration management needed by all other components
- Terminal UI components used by monitoring and user interaction
- Queue management system affects all API calls
- Caching layer impacts API calls and performance