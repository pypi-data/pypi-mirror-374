"""
Tests for the JyutpingTranscriber class.
"""

import pytest
from jyutping2characters.transcriber import JyutpingTranscriber


class TestJyutpingTranscriber:
    """Test cases for JyutpingTranscriber."""

    @pytest.fixture
    def sample_data(self):
        """Sample frequency data for testing."""
        return [
            # Single characters
            ("大", "daai6", 150.0),
            ("打", "daa2", 100.0),
            ("工", "gung1", 200.0),
            # homophone
            ("公", "gung1", 300.0),
            ("作", "zok3", 190.0),
            ("我", "ngo5", 1000.0),
            ("愛", "oi3", 800.0),
            ("你", "nei5", 900.0),
            ("今", "gam1", 500.0),
            ("日", "jat6", 400.0),
            
            # Multi-character words (higher frequency than components)
            ("工作", "gung1zok3", 500.0),
            ("今日", "gam1jat6", 800.0),
            ("我愛你", "ngo5oi3nei5", 300.0),
        ]

    @pytest.fixture
    def transcriber(self, sample_data):
        """Create a JyutpingTranscriber instance with sample data."""
        return JyutpingTranscriber(sample_data)

    def test_init_empty_data(self):
        """Test initialization with empty data raises ValueError."""
        with pytest.raises(ValueError, match="Frequency data cannot be empty"):
            JyutpingTranscriber([])

    def test_init_valid_data(self, sample_data):
        """Test successful initialization with valid data."""
        transcriber = JyutpingTranscriber(sample_data)
        assert transcriber.log_prob_dict is not None
        assert transcriber.max_word_len > 0

    def test_transcribe_empty_string(self, transcriber):
        """Test transcribing empty string returns empty string."""
        result = transcriber.transcribe("")
        assert result == ""

    def test_transcribe_single_character(self, transcriber):
        """Test transcribing single character."""
        result = transcriber.transcribe("ngo5")
        assert result == "我"

    def test_transcribe_phrase_prefers_common_words(self, transcriber):
        """Test that transcriber prefers common phrases over individual characters."""
        # "工作" should be preferred over "公" + "作"
        result = transcriber.transcribe("gung1zok3")
        assert result == "工作"
    
    def test_transcribe_long_phrase(self, transcriber):
        """Test transcribing longer phrases."""
        result = transcriber.transcribe("gam1jat6gung1zok3ngo5oi3nei5")
        assert result == "今日工作我愛你"

    def test_transcribe_unknown_input(self, transcriber):
        """Test transcribing gibberish input returns empty string."""
        result = transcriber.transcribe("george")
        assert result == ""

    def test_transcribe_partial_match(self, transcriber):
        """Test transcribing input with some unknown parts."""
        # Mix of known and unknown - should fail gracefully
        result = transcriber.transcribe("ngo5xyz")
        assert result == ""

    def test_max_word_len_calculation(self, sample_data):
        """Test that max_word_len is calculated correctly."""
        transcriber = JyutpingTranscriber(sample_data)
        expected_max = max(len(romanization) for _, romanization, _ in sample_data)
        assert transcriber.max_word_len == expected_max

    def test_duplicate_romanizations(self):
        """Test handling of multiple words with same romanization."""
        data_with_duplicates = [
            ("筆", "bat1", 100.0),
            ("不", "bat1", 200.0),  # Same romanization, different frequency
        ]
        transcriber = JyutpingTranscriber(data_with_duplicates)
        
        # Both should be in the dictionary
        assert "bat1" in transcriber.log_prob_dict
        assert len(transcriber.log_prob_dict["bat1"]) == 2
        
        # Should choose the more frequent one
        result = transcriber.transcribe("bat1")
        assert result == "不"
