# Jyutping2Characters

Convert Cantonese Jyutping romanization to Traditional Chinese characters.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

**Jyutping2Characters** is a Python library that converts Jyutping romanization (the standard romanization system for Cantonese) into Traditional Chinese characters. It uses the Viterbi algorithm to find the most probable sequence of Chinese characters based on word frequencies from real-world data.

The project follows the [Jyutping standard](https://jyutping.org/jyutping/) set by The Linguistic Society of Hong Kong Cantonese Romanization Scheme.

## Installation

```bash
pip install jyutping2characters
```

> [!WARNING]
> **First Run Notice**
> 
> On first use, this library downloads and processes mapping data from online sources (up to a minute). The data is then cached locally for instant subsequent use.

## Quick Start

```python
from jyutping2characters import transcribe

# Basic transcription
jyutping = "zou6jan4jyu4gwo2mou5mung6soeng2tung4tiu4haam4jyu2jau5me1fan1bit6" # 做人如果冇夢想同條鹹魚有咩分別

print(transcribe(jyutping))    # 我愛你
```

See the [`example/`](example/) directory for more examples.

## How It Works

The transcriber uses the **Viterbi algorithm** to find the optimal sequence of Chinese characters. It combines data from authoritative sources to build probabilistic models based on real-world usage frequencies, then finds the character/word/phrase segmentation that maximizes total probability.

```plaintext
# 只 is more common than 紙
zi2 -> 只
# 不 is more common than 筆
bat1 -> 不
# but 紙筆 is a common word, occurs more often than 只 and 不 standalone
zi2bat1 -> 紙筆
# word segmentation (我愛+粵拼)
ngo5oi3jyut6ping3 -> 我愛粵拼
# let's try a long sentence
# (做人+如果+冇+夢想+同條+鹹魚+有+咩+分別)
zou6jan4jyu4gwo2mou5mung6soeng2tung4tiu4haam4jyu2jau5me1fan1bit6 -> 做人如果冇夢想同條鹹魚有咩分別
```

> [!NOTE]
> As the model does not consider n-gram transitions between words, it may occasionally produce less natural results for ambiguous inputs. Future versions may incorporate more complex language models to improve accuracy.

## Logging Configuration

By default, the library operates silently. To see initialization progress:

```python
import logging
logging.basicConfig(level=logging.INFO)

from jyutping2characters import transcribe
result = transcribe("nei5hou2")  # Shows loading messages
```

## Command Line Interface

```bash
# Transcribe text
jyutping2characters transcribe "ngo5oi3nei5"

# Pre-load data for faster performance  
jyutping2characters warmup

# Show system information
jyutping2characters info
```

## Data Sources & Attribution

This project builds upon excellent open-source data from:

- [LSHK Jyutping Table](https://github.com/lshk-org/jyutping-table): Maintained by the Linguistic Society of Hong Kong, providing character-to-Jyutping mappings. ([CC-BY 4.0](https://github.com/lshk-org/jyutping-table/blob/master/LICENSE))
- [Rime Cantonese](https://github.com/rime/rime-cantonese): Part of the Rime Input Method Engine project, providing word frequencies and dictionary data. ([CC-BY 4.0](https://github.com/rime/rime-cantonese/blob/main/LICENSE-CC-BY) and [ODbL 1.0](https://github.com/rime/rime-cantonese/blob/main/LICENSE-ODbL))

Credits to the authors and contributors of these projects for making this work possible.

## License

[MIT License](LICENSE)

## Author
[James Zheng](https://linkedin.com/in/james-zheng-zi)
