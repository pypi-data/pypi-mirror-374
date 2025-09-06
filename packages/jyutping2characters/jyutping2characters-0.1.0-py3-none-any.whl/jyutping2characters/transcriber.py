"""
Jyutping to Chinese character transcriber using dynamic programming.

This module provides the JyutpingTranscriber class that converts Jyutping
romanization to Traditional Chinese characters using the Viterbi algorithm
for optimal sequence selection based on word frequencies.
"""

import json
import math
import collections
from typing import List, Tuple, Dict


class JyutpingTranscriber:
    """
    A tool to transcribe Jyutping romanization back to Traditional Chinese characters
    using a dynamic programming algorithm based on word/phrase frequencies.

    This implementation uses the Viterbi algorithm to find the most probable
    sequence of characters given a continuous string of romanized syllables.
    The "probability" of a sequence is calculated as the sum of the log
    probabilities of its constituent words/phrases, making it a "simple model"
    that does not rely on n-gram transition probabilities between words.

    Co-authored-by: G. Gemini
    """

    def __init__(self, frequency_data: List[Tuple[str, str, float]]) -> None:
        """
        Initializes the transcriber with the language data.

        Args:
            frequency_data: A list of tuples, where each tuple contains:
                (original_word: str, romanized_spelling: str, frequency: float)
                Example: [("你好", "neihao", 5000), ("好", "hou", 10000)]
        """
        if not frequency_data:
            raise ValueError("Frequency data cannot be empty.")
        
        # This dictionary will store the pre-calculated log probabilities.
        # The key is the romanized string, and the value is a list of
        # tuples: (original_word, log_probability).
        self.log_prob_dict = self._build_log_prob_dict(frequency_data)
        
        # Find the maximum possible length of a romanized word in our dictionary.
        # This is an optimization to avoid checking excessively long substrings.
        self.max_word_len = max(len(jyutping) for jyutping in self.log_prob_dict.keys())

    @classmethod
    def from_file(cls, data_path: str) -> 'JyutpingTranscriber':
        """
        Create a JyutpingTranscriber instance from a JSON data file.
        
        Args:
            data_path: Path to the JSON file containing frequency data
            
        Returns:
            JyutpingTranscriber instance
        """
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(data)

    def _build_log_prob_dict(self, frequency_data: List[Tuple[str, str, float]]) -> Dict[str, List[Tuple[str, float]]]:
        """
        Processes the raw frequency data into a lookup dictionary of log probabilities.
        Using log probabilities turns multiplication of probabilities into addition,
        which is numerically more stable and avoids floating-point underflow.
        """
        # Calculate the total frequency of all words/phrases in the corpus.
        total_frequency = sum(freq for _, _, freq in frequency_data)
        
        # defaultdict simplifies appending to lists for new keys.
        log_prob_dict = collections.defaultdict(list)
        
        for original_word, romanization, freq in frequency_data:
            if freq <= 0:
                # Frequencies must be positive to avoid log(0) errors.
                continue
            
            # P(word) = frequency(word) / total_frequency
            # We use the natural logarithm.
            log_prob = math.log(freq / total_frequency)
            log_prob_dict[romanization].append((original_word, log_prob))
            
        return dict(log_prob_dict)

    def transcribe(self, romanized_text: str) -> str:
        """
        Transcribes a romanized string into the most likely original character sequence.

        Args:
            romanized_text: The input Jyutping string to transcribe (e.g., "gam1jat6").

        Returns:
            The most probable transcription (e.g., "今日"). Returns an empty
            string if no valid transcription can be found.
        """
        if not romanized_text:
            return ""
            
        n = len(romanized_text)
        
        # scores[i] stores the max log probability of a transcription for the prefix of length i.
        scores = [-float('inf')] * (n + 1)
        scores[0] = 0.0  # The probability of an empty string is 1, so log(1) = 0.

        # backpointers[i] stores the start index of the last word in the optimal path to i.
        backpointers = [0] * (n + 1)
        
        # best_words[i] stores the actual original character/word for that last segment.
        best_words = [''] * (n + 1)

        # --- Forward Pass: Build the probability lattice ---
        # Iterate through each possible end position in the string.
        for j in range(1, n + 1):
            # Iterate through each possible start position for a word ending at j.
            # We add an optimization to not check substrings longer than our longest known word.
            start_range = max(0, j - self.max_word_len)
            for i in range(start_range, j):
                substring = romanized_text[i:j]
                
                if substring in self.log_prob_dict:
                    # This substring is a valid romanization for one or more words.
                    for original_word, log_prob in self.log_prob_dict[substring]:
                        # The score of this path is the score to get to the start of
                        # the current word (scores[i]) plus the score of the current word itself.
                        candidate_score = scores[i] + log_prob
                        
                        # If we've found a better path to position j, update our tables.
                        if candidate_score > scores[j]:
                            scores[j] = candidate_score
                            backpointers[j] = i
                            best_words[j] = original_word
        
        # --- Backtracking: Reconstruct the best path ---
        if scores[n] == -float('inf'):
            # This means no valid sequence of words from our dictionary can form the input string.
            return ""
            
        result = []
        current_pos = n
        while current_pos > 0:
            # Get the word that ended at the current position.
            word = best_words[current_pos]
            result.append(word)
            # Jump back to the start of that word.
            current_pos = backpointers[current_pos]
        
        # The result was built backwards, so we reverse it.
        result.reverse()
        
        return "".join(result)


