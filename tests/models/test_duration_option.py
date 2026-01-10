"""
Tests for DurationOption Domain Model - Story 3.6

Test Groups:
- Group 1: DurationOption Dataclass (Task 1)
- Group 2: Duration Calculations

Test IDs: N/A (Domain model tests)
"""
import pytest


# =============================================================================
# Test Group 1: DurationOption Dataclass (Task 1)
# =============================================================================

class TestDurationOptionDataclass:
    """Tests for DurationOption dataclass creation and fields."""

    def test_duration_option_can_be_imported(self):
        """[P0] DurationOption should be importable from models.domain module.
        
        Validates module structure is correct.
        """
        # Given: The models.domain module exists
        # When: Importing DurationOption from models.domain
        from eleven_video.models.domain import DurationOption
        
        # Then: DurationOption should exist
        assert DurationOption is not None

    def test_duration_option_creation_with_all_fields(self):
        """[P0] DurationOption can be created with all required fields."""
        # Given: Duration option parameters
        from eleven_video.models.domain import DurationOption
        
        # When: Creating a DurationOption
        option = DurationOption(minutes=5, label="Standard", description="~5 minutes")
        
        # Then: All fields should be accessible
        assert option.minutes == 5
        assert option.label == "Standard"
        assert option.description == "~5 minutes"

    def test_duration_option_creation_with_default_description(self):
        """[P1] DurationOption can be created with default empty description."""
        # Given: Duration option parameters without description
        from eleven_video.models.domain import DurationOption
        
        # When: Creating a DurationOption without description
        option = DurationOption(minutes=3, label="Short")
        
        # Then: Description should default to empty string
        assert option.description == ""


# =============================================================================
# Test Group 2: Duration Calculations (Task 1.3)
# =============================================================================

class TestDurationOptionCalculations:
    """Tests for DurationOption estimated calculations."""

    def test_estimated_word_count_for_3_minutes(self):
        """[P0] [3.6-UNIT-001] 3-minute duration should estimate 450 words.
        
        Story requirement: 150 words/minute.
        """
        # Given: A 3-minute duration option
        from eleven_video.models.domain import DurationOption
        option = DurationOption(minutes=3, label="Short")
        
        # When: Getting estimated word count
        word_count = option.estimated_word_count
        
        # Then: Should be 3 * 150 = 450 words
        assert word_count == 450

    def test_estimated_word_count_for_5_minutes(self):
        """[P0] [3.6-UNIT-001] 5-minute duration should estimate 750 words."""
        # Given: A 5-minute duration option
        from eleven_video.models.domain import DurationOption
        option = DurationOption(minutes=5, label="Standard")
        
        # When: Getting estimated word count
        word_count = option.estimated_word_count
        
        # Then: Should be 5 * 150 = 750 words
        assert word_count == 750

    def test_estimated_word_count_for_10_minutes(self):
        """[P0] [3.6-UNIT-001] 10-minute duration should estimate 1500 words."""
        # Given: A 10-minute duration option
        from eleven_video.models.domain import DurationOption
        option = DurationOption(minutes=10, label="Extended")
        
        # When: Getting estimated word count
        word_count = option.estimated_word_count
        
        # Then: Should be 10 * 150 = 1500 words
        assert word_count == 1500

    def test_estimated_image_count_for_3_minutes(self):
        """[P0] [3.6-UNIT-001] 3-minute duration should estimate 45 images.
        
        Story requirement: 15 images/minute (at ~4 seconds per image).
        """
        # Given: A 3-minute duration option
        from eleven_video.models.domain import DurationOption
        option = DurationOption(minutes=3, label="Short")
        
        # When: Getting estimated image count
        image_count = option.estimated_image_count
        
        # Then: Should be 3 * 15 = 45 images
        assert image_count == 45

    def test_estimated_image_count_for_5_minutes(self):
        """[P0] [3.6-UNIT-001] 5-minute duration should estimate 75 images."""
        # Given: A 5-minute duration option
        from eleven_video.models.domain import DurationOption
        option = DurationOption(minutes=5, label="Standard")
        
        # When: Getting estimated image count
        # Then: Should be 5 * 15 = 75 images
        assert option.estimated_image_count == 75

    def test_estimated_image_count_for_10_minutes(self):
        """[P0] [3.6-UNIT-001] 10-minute duration should estimate 150 images."""
        # Given: A 10-minute duration option
        from eleven_video.models.domain import DurationOption
        option = DurationOption(minutes=10, label="Extended")
        
        # When: Getting estimated image count
        # Then: Should be 10 * 15 = 150 images
        assert option.estimated_image_count == 150


# =============================================================================
# Test Group 3: DURATION_OPTIONS and Constants
# =============================================================================

class TestDurationConstants:
    """Tests for predefined duration constants."""

    def test_duration_options_can_be_imported(self):
        """[P0] DURATION_OPTIONS should be importable from models.domain."""
        # Given: The models.domain module
        # When: Importing DURATION_OPTIONS
        from eleven_video.models.domain import DURATION_OPTIONS
        
        # Then: DURATION_OPTIONS should be a list
        assert isinstance(DURATION_OPTIONS, list)

    def test_duration_options_has_three_presets(self):
        """[P0] DURATION_OPTIONS should have 3 preset durations."""
        # Given: The DURATION_OPTIONS constant
        from eleven_video.models.domain import DURATION_OPTIONS
        
        # When: Checking length
        # Then: Should have exactly 3 presets (3, 5, 10 minutes)
        assert len(DURATION_OPTIONS) == 3

    def test_duration_options_contain_3_5_10_minutes(self):
        """[P0] DURATION_OPTIONS should contain 3, 5, and 10 minute presets."""
        # Given: The DURATION_OPTIONS constant
        from eleven_video.models.domain import DURATION_OPTIONS
        
        # When: Extracting minutes values
        minutes_values = [opt.minutes for opt in DURATION_OPTIONS]
        
        # Then: Should contain 3, 5, and 10
        assert 3 in minutes_values
        assert 5 in minutes_values
        assert 10 in minutes_values

    def test_default_duration_minutes_can_be_imported(self):
        """[P0] DEFAULT_DURATION_MINUTES should be importable from models.domain."""
        # Given: The models.domain module
        # When: Importing DEFAULT_DURATION_MINUTES
        from eleven_video.models.domain import DEFAULT_DURATION_MINUTES
        
        # Then: DEFAULT_DURATION_MINUTES should be defined (typically 5)
        assert isinstance(DEFAULT_DURATION_MINUTES, int)

    def test_default_duration_minutes_is_5(self):
        """[P0] DEFAULT_DURATION_MINUTES should be 5 (standard duration)."""
        # Given: The DEFAULT_DURATION_MINUTES constant
        from eleven_video.models.domain import DEFAULT_DURATION_MINUTES
        
        # When: Checking value
        # Then: Should be 5 minutes (as per story design)
        assert DEFAULT_DURATION_MINUTES == 5


# =============================================================================
# Test Group 4: VideoDuration Enum
# =============================================================================

class TestVideoDurationEnum:
    """Tests for VideoDuration enum."""

    def test_video_duration_enum_can_be_imported(self):
        """[P1] VideoDuration enum should be importable from models.domain."""
        # Given: The models.domain module
        # When: Importing VideoDuration
        from eleven_video.models.domain import VideoDuration
        
        # Then: VideoDuration should exist
        assert VideoDuration is not None

    def test_video_duration_enum_has_short_value(self):
        """[P1] VideoDuration.SHORT should be 3 minutes."""
        # Given: The VideoDuration enum
        from eleven_video.models.domain import VideoDuration
        
        # When: Getting SHORT value
        # Then: Should be 3
        assert VideoDuration.SHORT.value == 3

    def test_video_duration_enum_has_standard_value(self):
        """[P1] VideoDuration.STANDARD should be 5 minutes."""
        # Given: The VideoDuration enum
        from eleven_video.models.domain import VideoDuration
        
        # When: Getting STANDARD value
        # Then: Should be 5
        assert VideoDuration.STANDARD.value == 5

    def test_video_duration_enum_has_extended_value(self):
        """[P1] VideoDuration.EXTENDED should be 10 minutes."""
        # Given: The VideoDuration enum
        from eleven_video.models.domain import VideoDuration
        
        # When: Getting EXTENDED value
        # Then: Should be 10
        assert VideoDuration.EXTENDED.value == 10
