# SIGRID Systems Python Client

Python client library for SIGRID legal analysis API.

## Installation
```bash
pip install sigrid-systems
```

## Usage
```python
from sigrid.systems import client, types

api_client = client.Client(api_key="your-key", user_id="user-123")
async with api_client.analyze_stream(documents, query) as stream:
    async for event in stream:
        print(event.type)
```

## Documentation
See full documentation at https://docs.sigrid-systems.com