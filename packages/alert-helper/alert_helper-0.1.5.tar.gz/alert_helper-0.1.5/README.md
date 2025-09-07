# Simple Python Notification Helper

## Supported Apps
### Slack
- After obtaining a webhook URL from Slack, set it as the `SLACK_WEBHOOK_URL` environment variable.

## Usage
- Context manager
```python
from alert_helper import alert

with alert("test-job"):
    # do something
```

- Decorator
```python
from alert_helper import alert

@alert("test-job")
def dummy():
    # do something

dummy()
```

- Only alert when there is an error
```python
from alert_helper import alert

with alert("test-job", on="error"):
    # do something
```

## To Do
- [ ] Support other apps.