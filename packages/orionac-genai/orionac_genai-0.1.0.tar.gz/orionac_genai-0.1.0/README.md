Orionac AI Python SDK
<p align="center">
<a href="#">
<img src="https://www.google.com/search?q=https://placehold.co/400x150/000000/FFFFFF%3Ftext%3DOrionac%2BAI" alt="Orionac AI Logo">
</a>
</p>

<p align="center">
<em>The official Python package to access the full power of Theta-1.0-sl directly in your application.</em>
</p>

Introduction
Welcome to the orionac-ai Python SDK! This package provides a simple, straightforward, and powerful way to integrate the Orionac AI Theta models into your Python applications.

Installation
The quickest way to get started is by installing our official Python package using pip.

pip install orionac-ai

Quickstart
Using the SDK is designed to be intuitive. Authenticate with your API key and start generating content in just a few lines of code.

# example.py
from orionac_ai import Theta

# Authenticate with your API key
# You can also set the ORIONAC_API_KEY environment variable
theta = Theta(api_key="YOUR_API_KEY")

# Generate sales content
response = theta.generate(
  prompt="Draft a follow-up email to a prospect we spoke with.",
  context={
    "prospect_name": "Jane Doe",
    "last_contact": "2 days ago",
    "topic": "Our new AI analytics platform"
  }
)

# Print the generated text
print(response.text)

# Access other response data
print(f"\nModel Used: {response.model_used}")
print(f"Total Tokens: {response.total_tokens}")

Expected Output
Subject: Following Up

Hi Jane Doe,

Just wanted to quickly follow up on our conversation from 2 days ago regarding our new AI analytics platform. Let me know if you have any further questions!

Best regards,
[Your Name]

Model Used: theta-1.0-sl
Total Tokens: 85

Advanced Usage
The generate method comes with over 20 parameters to give you fine-grained control over the output.

response = theta.generate(
  prompt="Generate three creative taglines for a coffee shop.",
  # --- Control Parameters ---
  temperature=0.9,
  max_tokens=100,
  stop_sequences=["\n4."],
  # --- Custom Attributes ---
  tone="witty",
  response_length="short"
)

print(response.text)

Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue.

License
This project is licensed under the MIT License.