# Oxidize

High-performance data processing tools for Python, built with Rust.

## Philosophy

Python data tools often require choosing between performance, installation simplicity, and parallel processing. These tools address that by providing:

- **Performance**: Rust implementation with 2-10x speed improvements
- **Easy installation**: Pre-built wheels, no compilation required
- **True parallelism**: GIL release for concurrent processing
- **Practical focus**: Solutions for common data engineering tasks

## Tools

### [oxidize-postal](https://github.com/yourusername/oxidize-postal)
Address parsing and normalization with international support.

```python
import oxidize_postal

parsed = oxidize_postal.parse_address("781 Franklin Ave Brooklyn NY 11216")
# {'house_number': '781', 'road': 'franklin ave', 'city': 'brooklyn', 'state': 'ny', 'postcode': '11216'}

expansions = oxidize_postal.expand_address("123 Main St NYC NY")
# ['123 main street nyc new york', '123 main street nyc ny', ...]
```

Improvements over pypostal:
- pip install with pre-built wheels (no C compilation)
- GIL released for parallel processing
- Single module API
- Cross-platform support

### [oxidize-xml](https://github.com/yourusername/oxidize-xml)
Streaming XML to JSON conversion for large files.

```python
import oxidize_xml

# Extract repeated elements to JSON Lines
count = oxidize_xml.parse_xml_file_to_json_file("data.xml", "book", "output.jsonl")

# Stream processing for large files
json_lines = oxidize_xml.parse_xml_file_to_json_string("export.xml", "record")
```

Improvements over lxml:
- 2-3x faster streaming parser
- Processes files larger than available RAM
- Consistent schema output for data analysis
- Built-in XML security protections

## Technical Approach

**Rust + PyO3**: Combines Rust's performance and memory safety with Python's ecosystem integration.

**GIL Release**: All compute operations release Python's Global Interpreter Lock, enabling true parallel processing in threaded environments.

**Streaming Architecture**: Designed for processing large datasets without loading everything into memory.

**Pre-built Wheels**: Cross-platform distribution eliminates compilation requirements and system dependencies.

## Use Cases

- ETL pipelines with address normalization
- Processing large XML exports and API responses
- Data cleaning workflows requiring parallel processing
- Web services handling structured data parsing

## Future Tools

Planned additions following the same principles:
- oxidize-csv: High-performance CSV processing
- oxidize-json: Streaming JSON operations
- oxidize-regex: Parallel text processing

## Contributing

Each tool has its own repository with specific contribution guidelines. General focus areas:
- Performance improvements with benchmarks
- API usability for common workflows
- Documentation and examples
- Test coverage for edge cases

## License

MIT License for all tools.