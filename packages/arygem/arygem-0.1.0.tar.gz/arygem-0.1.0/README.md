# AryGem

AryGem is a minimal Python wrapper for **Google Gemini AI** that makes it super easy to generate AI responses with just a few lines of code.  

---

## Installation

```bash
pip install arygem
````

---

## Usage

```python
from arygem import AryGem

# Initialize with your Gemini API key
client = AryGem("YOUR_GEMINI_API_KEY")

# Generate a response
answer = client.generate(
    "Tell me something interesting about cats.",
    context="Cats are small, furry mammals known for their agility."
)

print(answer)
```

---

## Features

* Simple and minimal setup
* Supports optional context to guide AI responses
* Uses Google Gemini default model (`gemini-2.5-flash`)
* Ready to use out-of-the-box

---

## Requirements

* Python >= 3.9
* `google-genai` library (installed automatically with AryGem)

---

## License

MIT License


This is **ready to use for PyPI** or GitHub — clean, concise, and user-friendly.  

If you want, Aryan, I can **also make an extended version with examples for batch queries and optional parameters** to make it look more professional. Do you want me to do that?
