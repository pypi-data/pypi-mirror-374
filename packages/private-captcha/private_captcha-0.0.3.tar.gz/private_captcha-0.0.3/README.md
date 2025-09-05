# private-captcha-py

Python client for server-side verification of Private Captcha solutions.

## Installation

```bash
pip install private-captcha
```

## Quick Start

```python
from private_captcha import Client

# Initialize the client with your API key
client = Client(api_key="your-api-key-here")

# Verify a captcha solution
try:
    result = client.verify(solution="user-solution-from-frontend")
    if result.success:
        print("Captcha verified successfully!")
    else:
        print(f"Verification failed: {result}")
except Exception as e:
    print(f"Error: {e}")
```

## Usage

### Web Framework Integration

#### Flask Example

```python
from flask import Flask, request
from private_captcha import Client, SolutionError

app = Flask(__name__)
client = Client(api_key="your-api-key")

@app.route('/submit', methods=['POST'])
def submit_form():
    try:
        # Verify captcha from form data
        client.verify_request(request.form)

        # Process your form data here
        return "Form submitted successfully!"

    except SolutionError:
        return "Captcha verification failed", 400
```

#### Django Example

```python
from django.http import HttpResponse
from private_captcha import Client, SolutionError

client = Client(api_key="your-api-key")

def submit_view(request):
    if request.method == 'POST':
        try:
            client.verify_request(request.POST)
            # Process form data
            return HttpResponse("Success!")
        except SolutionError:
            return HttpResponse("Captcha failed", status=400)
```

## Configuration

### Client Options

```python
from private_captcha import Client, EU_DOMAIN

client = Client(
    api_key="your-api-key",
    domain=EU_DOMAIN,                       # replace domain for self-hosting or EU isolation
    form_field="private-captcha-solution",  # custom form field name
    timeout=10.0,                           # request timeout in seconds
)
```

### Non-standard backend domains

```python
from private_captcha import Client, EU_DOMAIN

# Use EU domain
eu_client = Client(
    api_key="your-api-key",
    domain=EU_DOMAIN  # api.eu.privatecaptcha.com
)

# Or specify custom domain in case of self-hosting
custom_client = Client(
    api_key="your-api-key", 
    domain="your-custom-domain.com"
)
```

### Retry Configuration

```python
result = client.verify(
    max_backoff_seconds=15,  # maximum wait between retries
    attempts=3               # number of retry attempts
)
```

## Requirements

- Python 3.9+
- No external dependencies (uses only standard library)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues with this Python client, please open an issue on GitHub.
For Private Captcha service questions, visit [privatecaptcha.com](https://privatecaptcha.com).
