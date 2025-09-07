# Oxidize

High-performance data processing tools for Python, built with Rust.

## Philosophy

- **Best of both worlds**: Python interfaces with Rust backends for both simplicity and performance
- **True parallelism**: GIL release for concurrent processing
- **Easy installation**: Pre-built wheels, no compilation required
- **Practical**: Specialized solutions for common data engineering tasks

## Tools

### [oxidize-postal](https://github.com/ericaleman/oxidize-postal)
oxidize-postal is an alternative to pypostal for Python bindings of the libpostal library, which provides address parsing and normalization with international support. 

oxidize-postal provides the same address parsing capabilities as pypostal but addresses key limitations: it installs without C compilation, releases the Python GIL for true parallel processing, and offers a cleaner API. Built using Rust and libpostal-rust bindings to the libpostal C library.

```python
import oxidize_postal

parsed = oxidize_postal.parse_address("781 Franklin Ave Brooklyn NY 11216")
# {'house_number': '781', 'road': 'franklin ave', 'city': 'brooklyn', 'state': 'ny', 'postcode': '11216'}

expansions = oxidize_postal.expand_address("123 Main St NYC NY")
# ['123 main street nyc new york', '123 main street nyc ny', ...]
```

### [oxidize-xml](https://github.com/ericaleman/oxidize-xml)
oxidize-xml is an alternative to lxml and provides streaming XML to JSON conversion for large files.

oxidize-xml is more specialized and opiniated, focusing on common data engineering workflows for extracting repeated elements from large XML files like API responses, log files, and data exports, is particularly built for engineers and analysts working in DuckDB or Polars.

```python
import oxidize_xml

# Extract repeated elements to JSON Lines
count = oxidize_xml.parse_xml_file_to_json_file("data.xml", "book", "output.jsonl")

# Stream processing for large files
json_lines = oxidize_xml.parse_xml_file_to_json_string("export.xml", "record")
```

## Future Tools

New versions to oxidize-xml / oxidize-postal plus new packages coming soon.

## License

MIT License for all tools.