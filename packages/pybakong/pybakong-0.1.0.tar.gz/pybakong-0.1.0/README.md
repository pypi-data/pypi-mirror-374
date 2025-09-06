
# pybakong

Python SDK for Cambodia Bakong Open API.

## Installation

```bash
pip install pybakong
```

## Usage

```python
from pybakong import BakongClient

client = BakongClient()

# Step 1: Request token
client.request_token("your@email.com", "MyOrg", "MyProject")

# Step 2: Verify token with code from email
client.verify_token("123456")

# Step 3: Generate deeplink
link = client.generate_deeplink(
    qr="QR_STRING",
    app_icon_url="https://example.com/icon.png",
    app_name="MyApp",
    app_deep_link_callback="myapp://callback"
)
print("Payment Link:", link)
```
