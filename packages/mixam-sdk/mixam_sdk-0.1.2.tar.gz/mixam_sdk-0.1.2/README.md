# Mixam Python SDK

Mixam SDK is a lightweight Python library that helps you build, validate, serialize, and parse print Item Specifications used by Mixam. It provides:

- Core data models and enums to represent product specifications (components, substrates, bindings, sizes, etc.).
- A Universal Key system to serialize an ItemSpecification to a compact string and parse it back reliably.

## Installation

- Via pip:

```bash
pip install mixam-sdk
```

- Via Poetry:

```bash
poetry add mixam-sdk
```

Python 3.13+ is required (see `pyproject.toml`).

## Quick Start

Below are minimal examples showing how to work with Item Specifications and the Universal Key.

### Create an ItemSpecification and build a Universal Key

```python
from mixam_sdk.item_specification.models.item_specification import ItemSpecification
from mixam_sdk.item_specification.enums.product import Product
from mixam_sdk.item_specification.models.flat_component import FlatComponent
from mixam_sdk.item_specification.enums.component_type import ComponentType
from mixam_sdk.universal_key.models.key_builder import KeyBuilder

# Build a simple spec with one flat component
item = ItemSpecification()
item.copies = 250

# Create a simple flat component
comp = FlatComponent()
comp.component_type = ComponentType.FLAT
# ... populate additional fields supported by FlatComponent as needed ...

item.components.append(comp)

# Build a Universal Key string
key = KeyBuilder().build(item)
print(key)
```

### Parse a Universal Key back into an ItemSpecification

```python
from mixam_sdk.universal_key.models.key_parser import KeyParser

parser = KeyParser()
# Provide a Universal Key string (from earlier build step or an external source)
some_key = "250~10-fl{...}"
parsed = parser.parse(some_key)

print(parsed.copies)
print(parsed.product)
print([c.component_type for c in parsed.components])
```

If the key does not match the expected format, `KeyParser.parse` raises a `ValueError` or `RuntimeError` indicating the issue.

## What is a Universal Key?

A Universal Key is a compact, validated string representation of an `ItemSpecification`.

- Format (high level):
  - `copies~productId-<component>{<memberTokens>}-<component>{...}`
- Example: `250~10-fl{...}-bd{...}`
- Keys are validated using a strict regex to ensure correctness before parsing.

The SDK provides:

- `KeyBuilder` to generate keys from `ItemSpecification` objects.
- `KeyParser` to parse keys back into `ItemSpecification` objects.

## Main Concepts

- Enums: Found under `mixam_sdk/item_specification/enums`, they define allowed values for products, sizes, colours, laminations, bindings, etc.
- Models: Under `mixam_sdk/item_specification/models`, they represent components such as flat, folded, cover, bound components, and more, as well as the root `ItemSpecification`.
- Interfaces/Support: Internal helpers for ordering components and mapping model fields to the Universal Key token format.

Explore the `tests/` folder for concrete usage patterns and expected behaviours:

- `tests/test_universal_key.py`
- `tests/test_item_specification_deserialization.py`

## Error Handling

- `KeyParser.parse(key)` validates input and raises a `ValueError` for invalid format and a `RuntimeError` for parsing failures.
- When building keys, ensure your components are populated with required fields; otherwise the builder may not emit expected tokens.

## Development

- Run tests:

```bash
pytest -q
```

- Local install for development:

```bash
poetry install
poetry run pytest -q
```

## Versioning

The package follows semantic versioning where possible. See `pyproject.toml` for the current version.

## License

Copyright (c) Mixam.

See the repository for license terms or contact developer@mixam.com.

## Examples (from tests)

Below are full examples taken directly from the test suite to illustrate the exact formats.

- Universal Key example (Booklet):

```
10~1-bd{4bt-5c-4f-200p-1st-3sw}-cr{5c-5c+-4f-4l-1st-7sw}
```

- Matching ItemSpecification JSON example (as used in tests):

```json
{
  "itemSpecification": {
    "copies": 10,
    "product": "BROCHURES",
    "components": [
      {
        "componentType": "BOUND",
        "format": 4,
        "standardSize": "NONE",
        "orientation": "PORTRAIT",
        "colours": "PROCESS",
        "substrate": {
          "typeId": 1,
          "weightId": 3,
          "colourId": 0
        },
        "pages": 200,
        "lamination": "NONE",
        "binding": {
          "type": "PUR"
        }
      },
      {
        "componentType": "COVER",
        "format": 4,
        "standardSize": "NONE",
        "orientation": "PORTRAIT",
        "colours": "PROCESS",
        "substrate": {
          "typeId": 1,
          "weightId": 7,
          "colourId": 0
        },
        "lamination": "GLOSS",
        "backColours": "PROCESS",
        "backLamination": "NONE"
      }
    ]
  }
}
```

## Links

- Source: https://github.com/mixam-platform/mixam-python-sdk
- Mixam: https://mixam.com
