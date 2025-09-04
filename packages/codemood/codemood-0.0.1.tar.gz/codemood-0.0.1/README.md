# 🌀 Codemood

> *“Because even code has feelings…”*

[![PyPI version](https://img.shields.io/pypi/v/codemood.svg?color=blue)](https://pypi.org/project/codemood/)
[![PyPI downloads](https://img.shields.io/pypi/dm/codemood.svg?color=green)](https://pypi.org/project/codemood/)
[![License](https://img.shields.io/github/license/OmkarPalika/codemood.svg?color=yellow)](https://github.com/OmkarPalika/codemood/blob/main/LICENSE)
[![Build](https://img.shields.io/github/actions/workflow/status/OmkarPalika/codemood/python-package.yml?branch=main)](https://github.com/OmkarPalika/codemood/actions)
[![Made with ❤️](https://img.shields.io/badge/made%20with-%F0%9F%96%A4-red)](https://github.com/OmkarPalika/codemood)

Codemood is a lighthearted Python package that **analyzes the “mood” of your code**.
Under the hood, it uses AI sentiment analysis — but instead of just saying *positive/negative*, it explains *why* your code snippet made the model happy, sad, or confused.

Perfect for:<br>
✅ Adding humor to coding sessions<br>
✅ Live demos & hackathons<br>
✅ Side projects that surprise developers with witty feedback

---

## ✨ Features

* 🚀 Works out-of-the-box (no setup needed).
* 🧠 Uses Hugging Face Transformers locally if available.
* ☁️ Falls back to Hugging Face API (if you provide `HF_TOKEN`).
* 🎭 Funny explanations — not just *“Positive”*, but *“Model got happy because it saw print 🎉”*.
* 🐍 Lightweight, pip-installable, hackathon-friendly.

---

## 📦 Installation

```bash
pip install codemood
```

---

## ⚡ Quickstart

```python
from codemood import analyze_code

snippet = "for i in range(10): print(i)"
mood = analyze_code(snippet)

print(mood)
```

**Output:**

```python
{
  'label': 'POSITIVE',
  'score': 0.98,
  'reason': "Model got happy because it saw print 🎉"
}
```

---

## 🎯 Advanced Usage

```python
from codemood import CodeMoodAnalyzer

analyzer = CodeMoodAnalyzer()

# Analyze a function
code = """
def greet(name):
    print("Hello", name)
"""
print(analyzer.analyze(code))

# Alias method (same result)
print(analyzer.explain_sentiment(code))
```

---

## 🔑 Hugging Face API (Optional)

By default, Codemood works offline with `transformers`.<br>If you want cloud inference, set your Hugging Face token:

```bash
export HF_TOKEN="your_hf_token_here"
```

No token? No worries → Codemood will gracefully skip cloud mode.

---

## 🛠️ Roadmap

* [ ] Add more “emotions” beyond positive/negative.
* [ ] Language-specific code mood tuning (Python vs JS vs C++).
* [ ] VS Code extension for live code mood popups.

---

## 🤝 Contributing

PRs are welcome! Fork the repo, create a branch, and send a PR with your funniest improvements.

---

## 📜 License

MIT — Free to use, remix, and make your code smile 😄

---

🔥 With **Codemood**, your code reviews will never be boring again.

---
A4-red)](https://github.com/OmkarPalika/codemood)

Codemood is a lighthearted Python package that **analyzes the “mood” of your code**.
Under the hood, it uses AI sentiment analysis — but instead of just saying *positive/negative*, it explains *why* your code snippet made the model happy, sad, or confused.

Perfect for:<br>
✅ Adding humor to coding sessions<br>
✅ Live demos & hackathons<br>
✅ Side projects that surprise developers with witty feedback

---

## ✨ Features

* 🚀 Works out-of-the-box (no setup needed).
* 🧠 Uses Hugging Face Transformers locally if available.
* ☁️ Falls back to Hugging Face API (if you provide `HF_TOKEN`).
* 🎭 Funny explanations — not just *“Positive”*, but *“Model got happy because it saw print 🎉”*.
* 🐍 Lightweight, pip-installable, hackathon-friendly.

---

## 📦 Installation

```bash
pip install codemood
```

---

## ⚡ Quickstart

```python
from codemood import analyze_code

snippet = "for i in range(10): print(i)"
mood = analyze_code(snippet)

print(mood)
```

**Output:**

```python
{
  'label': 'POSITIVE',
  'score': 0.98,
  'reason': "Model got happy because it saw print 🎉"
}
```

---

## 🎯 Advanced Usage

```python
from codemood import CodeMoodAnalyzer

analyzer = CodeMoodAnalyzer()

# Analyze a function
code = """
def greet(name):
    print("Hello", name)
"""
print(analyzer.analyze(code))

# Alias method (same result)
print(analyzer.explain_sentiment(code))
```

---

## 🔑 Hugging Face API (Optional)

By default, Codemood works offline with `transformers`.<br>If you want cloud inference, set your Hugging Face token:

```bash
export HF_TOKEN="your_hf_token_here"
```

No token? No worries → Codemood will gracefully skip cloud mode.

---

## 🛠️ Roadmap

* [ ] Add more “emotions” beyond positive/negative.
* [ ] Language-specific code mood tuning (Python vs JS vs C++).
* [ ] VS Code extension for live code mood popups.

---

## 🤝 Contributing

PRs are welcome! Fork the repo, create a branch, and send a PR with your funniest improvements.

---

## 📜 License

MIT — Free to use, remix, and make your code smile 😄

---

🔥 With **Codemood**, your code reviews will never be boring again.

---
