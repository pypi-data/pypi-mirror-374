# Streamlit Google Analytics Tag (gtag)

A Streamlit component that allows you to integrate Google Analytics by tag and send events to Google Analytics.

## Installation

```bash
pip install streamlit-google-analytics-tag
```

## Usage

```python
import streamlit as st
from streamlit_gtag import st_gtag

# Initialize Google Analytics
st_gtag(
    gtag_id="GA_MEASUREMENT_ID",
    config={
        "send_page_view": True
    }
)

# Send custom events
st_gtag(
    event="custom_event",
    parameters={
        "event_category": "engagement",
        "event_label": "button_click"
    }
)
```

## Features

- Easy integration with Google Analytics 4
- Support for custom events
- Streamlit-native component
- Lightweight and fast

## License

MIT License
