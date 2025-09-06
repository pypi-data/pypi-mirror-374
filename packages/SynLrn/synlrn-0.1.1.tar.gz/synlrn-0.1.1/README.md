
---

# SynLrn – Modular Multi-Stage Learning for AI (No Naming or Structure Restrictions)

## Overview

**SynLrn** is a production-ready, modular system for context-based learning memory and retrieval—designed for any AI or agent workflow.
SynLrn supports any number of **custom learning stages**, adapts to your data, and makes context recall fast and simple—**no naming, schema, or vendor constraints.**

**Highlights:**

* **Any learning stages you want:** Use any stage names or workflow steps (thinking, clarifying, etc.)
* **No format restrictions:** Structure your learned data and knowledge base how you want.
* **No external server:** Everything runs locally, uses fast SQLite and RapidFuzz.
* **Plug-in knowledge base:** Start empty or preload with your own examples.
* **Works with all frameworks:** Use SynLrn in any Python project, agent, or LLM pipeline.

---

## Why SynLrn?

Traditional “memory” frameworks force you to:

* Use their schema, stage names, or folder structures.
* Fit your workflow to *their* definitions.
* Often require a server, specific model, or fixed APIs.

**SynLrn:**

* **Lets you define your own learning flow**—no hard-coded stage names, no schema lock-in.
* **Loads any data, any way:** Add, group, and recall examples however you want.
* **Keeps you in control:** Your workflow, your code, your memory.

---

## Key Features

* **Flexible stage loading:** Use any number of workflow stages.
* **Pluggable knowledge base:** Point to your own Python modules or classes.
* **Context-based retrieval:** RapidFuzz for fast, fuzzy example recall.
* **Low token use:** Matches and retrievals use minimal tokens, ideal for LLMs instead of providing full examples. in one shot SynLrn retrieves relevant examples based on context.
* **Minimal, direct API:** No setup bloat or function call ceremony.

---

## Example Layout (ALL valid)

```
project_root/
├── SLKnowledgebase/
│   └── Knowledgebase.py  # Your example base (optional)
├── .env
├── app.py
└── ...
```

Or any layout you prefer—**no requirements**.

---

## How It Works

1. **You define your workflow stages.**
2. **Store and retrieve context/response examples** per stage, for any purpose.
3. **Recall examples by context** (with fallbacks if needed).

---

## Example Usage

```python
from SynLrn import SynLrn

stages = [
    "thinking", "clarifying", "gathering",
    "defining", "refining", "reflecting", "decision"
]

fallbacks = {
    "thinking": [
        "user:\nWhat can you do?\n\nassistant:\nI can help with a wide variety of tasks, including..."
    ]
}

learn = SynLrn(stages=stages, fallbacks=fallbacks)

# Add a new memory/example
learn.addToLearned("thinking", "How do you work?", "I process your requests by reasoning over ...")

# Retrieve similar examples
results = learn.retrieveStage("How do you work?", "thinking")
for entry in results:
    print(entry)
```

**See full code and more examples on GitHub.**

---

## Customization

* **Knowledge base:**
  Optionally preload with your own class/module, any structure, any naming—SynLrn will find your example data automatically.

* **Fallbacks:**
  Pass a dict or a callable for custom fallback responses per stage.

* **Storage:**
  All learning is stored locally (SQLite, configurable directory).

---

## FAQ

**Q: Do I have to follow any naming or folder structure?**
A: **No.** Use any stage names, directory layout, or file names you want.

**Q: Can I use this in any Python agent, RAG, or LLM workflow?**
A: Yes.

**Q: Do I need a server, or does SynLrn require a specific cloud provider?**
A: No. Everything is local, pure Python.

---

## Code Examples

You can find code examples on my [GitHub repository](https://github.com/TristanMcBrideSr/TechBook).

---

## License

This project is licensed under the [Apache License, Version 2.0](LICENSE).
Copyright 2025 Tristan McBride Sr.

---

## Acknowledgements

Project by:
- Tristan McBride Sr.
- Sybil
