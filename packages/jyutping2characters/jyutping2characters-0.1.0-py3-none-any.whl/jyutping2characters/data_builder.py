"""
Data builder module for jyutping-transcriber.

This module handles downloading source data from online repositories,
processing it, and caching the results for efficient access.
"""

import csv
import json
import logging
import os
import urllib.request
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple
import appdirs

# Set up logging for the data builder module
logger = logging.getLogger(__name__)


def get_cache_dir() -> Path:
    """Get the cache directory for storing mapping data."""
    cache_dir = Path(appdirs.user_cache_dir("jyutping2characters"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_cached_data_path() -> Path:
    """Get the path to the cached mapping data file."""
    return get_cache_dir() / "mapping.json"


def ensure_data_available() -> str:
    """
    Ensure mapping data is available, building it if necessary.
    Returns the path to the data file.
    """
    data_path = get_cached_data_path()
    
    if not data_path.exists():
        logger.info("Building Jyutping mapping data from online sources")
        try:
            build_mapping_data(str(data_path))
            logger.info(f"Data cached successfully to: {data_path}")
        except Exception as e:
            logger.error(f"Failed to build data: {e}")
            raise
    
    return str(data_path)


def clear_cached_data() -> None:
    """Remove cached mapping data."""
    data_path = get_cached_data_path()
    if data_path.exists():
        data_path.unlink()
        logger.info("Cached data cleared")
    else:
        logger.info("No cached data found")


def download_file(url: str) -> str:
    """Download a file from URL and return its content as string."""
    logger.debug(f"Downloading: {url}")
    try:
        with urllib.request.urlopen(url) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        raise


def build_mapping_data(output_path: str) -> None:
    """
    Build the mapping data file from online sources.
    
    This function downloads data from:
    1. LSHK Jyutping Table - character to jyutping mappings
    2. Rime Cantonese Essay - word frequency data
    3. Rime Cantonese Dictionary - more words and word-jyutping mappings
    """
    # URLs for the data sources
    JYUTPING_TABLE_LIST_URL = 'https://raw.githubusercontent.com/lshk-org/jyutping-table/master/list.tsv'
    RIME_ESSAY_URL = 'https://raw.githubusercontent.com/rime/rime-cantonese/main/essay-cantonese.txt'
    RIME_DICT_URL = 'https://raw.githubusercontent.com/rime/rime-cantonese/main/jyut6ping3.words.dict.yaml'

    all_jyutping_mapping: Dict[str, str] = {}
    chars_jyutping_mapping: Dict[str, str] = {}

    # Step 1: Download and process LSHK Jyutping Table
    logger.debug("Processing LSHK Jyutping Table")
    list_tsv_content = download_file(JYUTPING_TABLE_LIST_URL)
    reader = csv.reader(reversed(list_tsv_content.splitlines()), delimiter='\t')
    
    char_count = 0
    for row in reader:
        if len(row) < 3:
            # invalid schema
            continue
        chars_jyutping_mapping[row[0]] = row[2]
        all_jyutping_mapping[row[0]] = row[2]
        char_count += 1
    
    logger.debug(f"Processed {char_count} character mappings")

    def get_jyutping(phrase: str) -> str | None:
        """Get jyutping for a phrase using character mappings."""
        jyutping = []
        for char in phrase:
            try:
                jyutping.append(chars_jyutping_mapping[char])
            except KeyError:
                # Skip phrases with unmapped characters
                return None
        return ''.join(jyutping)

    # Step 2: Download and process word frequency data
    logger.debug("Processing word frequency data")
    word_frequencies_map: Dict[str, int] = {}
    essay_content = download_file(RIME_ESSAY_URL)
    reader = csv.reader(essay_content.splitlines(), delimiter='\t')
    
    word_count = 0
    for row in reader:
        if len(row) != 2:
            # invalid schema
            continue
        word_frequencies_map[row[0]] = int(row[1])
        word = row[0]
        jyutping = get_jyutping(word)
        if jyutping:
            all_jyutping_mapping[word] = jyutping
            word_count += 1
    
    logger.debug(f"Processed {word_count} word frequency entries")

    # Step 3: Download and process Rime dictionary
    logger.debug("Processing Rime Cantonese dictionary")
    dict_content = download_file(RIME_DICT_URL)
    tsv_content = dict_content[dict_content.index('...') + 3:].strip()
    reader = csv.reader(reversed(tsv_content.splitlines()), delimiter='\t')
    
    dict_count = 0
    for row in reader:
        if len(row) < 2:
            # invalid schema
            continue
        # Ignore the x% column in the file because it's not needed
        word = row[0]
        jyutping = row[1].replace(' ', '')  # remove whitespace delimiters
        if jyutping:
            all_jyutping_mapping[word] = jyutping
            dict_count += 1
    
    logger.debug(f"Processed {dict_count} dictionary entries")

    # Step 4: Prepare final data structure
    logger.debug("Preparing final data structure")
    final_data: List[Tuple[str, str, float]] = []
    for word, jyutping in all_jyutping_mapping.items():
        frequency = word_frequencies_map.get(word, 0.1)  # default to 0.1 to avoid division by zero
        frequency = 0.1 if frequency == 0 else frequency  # also set to 0.1 if original frequency is zero
        final_data.append((word, jyutping, frequency))

    # Step 5: Write to output file
    logger.debug("Saving data to cache")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    # Write attribution file
    attribution_path = os.path.join(os.path.dirname(output_path), "ATTRIBUTION.txt")
    with open(attribution_path, "w", encoding='utf-8') as f:
        f.write("""jyutping2characters
Data built using the following sources:
- LSHK Jyutping Table (CC-BY 4.0)
  https://github.com/lshk-org/jyutping-table
- Rime Cantonese (CC-BY 4.0 and ODbL 1.0)
  https://github.com/rime/rime-cantonese
""")

    logger.info(f"Built mapping data with {len(final_data):,} entries")


if __name__ == "__main__":
    # For testing purposes
    output_path = get_cached_data_path()
    build_mapping_data(str(output_path))
    logger.info(f"Data built successfully: {output_path}")
