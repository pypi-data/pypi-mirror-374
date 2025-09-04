# Complex Text Tools

A Python package for processing complex text containing mixed Chinese and English characters, removing extra spaces and standardizing punctuation.

## Features

- Remove extra spaces between Chinese characters
- Remove extra spaces between Chinese and English characters
- Handle spacing around punctuation marks correctly
- Process mixed language texts efficiently

## Installation

```bash
pip install complex-text-tools
```

## Usage

```python
from complex_text_tools import remove_extra_spaces

text = "这 是  中文 测试  文本 ，  mixed  English  text  here ， 还 有   symbols :  ;  !  "
clean_text = remove_extra_spaces(text)
print(clean_text)
# Output: "这是中文测试文本，mixed English text here，还有 symbols:;!"
```

## License

This project is licensed under the MIT License.