# Simple Python Notification Helper

## Supported Apps
### Slack
- After obtaining a webhook URL from Slack, set it as the `SLACK_WEBHOOK_URL` environment variable.

## Usage
- Context manager
```python
from noticeme import noticeme

with noticeme("test-job"):
    # do something
```

- Decorator
```python
from noticeme import noticeme

@noticeme("test-job")
def dummy():
    # do something

dummy()
```

## To Do
- [ ] Support other apps.