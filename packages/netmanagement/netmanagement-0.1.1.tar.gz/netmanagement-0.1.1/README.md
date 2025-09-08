## Installation

```bash
pip install netmanagement
```

## Usage

```python
import netmanagement

response = netmanagement.get('https://httpbin.org/get')
print(response.status_code)
print(response.json())
```