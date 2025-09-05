# PyBugMate

**[PyPI-READY] Effortless, smart debugging and postmortem for every Python project. Track errors, see real data, get smart hints, and drop into a REPL instantly—zero setup!**

---

## ✨ Features

- Automatic error tracing: See which function crashed, with parameters and variable values.
- Colorful, instant logs: [CALL], [RETURN], [PROFILE], [EXCEPTION]—all clear and readable!
- Smart hints: Friendly, actionable tips for common Python mistakes.
- Drop-in postmortem: On any unhandled error, instantly debug in a live REPL (IPython shell).
- No config, zero boilerplate: Add two lines—works everywhere, from scripts to complex apps.

---

## 🚀 Installation

pip install pybugmate


## 🧑‍💻 Usage: Quick Start

Paste these lines at the top of your script:

### from pybugmate.postmortem import enable_postmortem
### from pybugmate.autowrap import autowrap

### enable_postmortem() # Step 1: Enable postmortem REPL for ANY unhandled crash!
### autowrap(globals()) # Step 2: Auto-wrap all your functions for smart tracing

---

## **💡 Why PyBugMate?**

- **Faster bug hunts:** Find errors instantly, with real context—no more `print` everywhere!
- **Perfect for learners:** You get helpful advice for real bugs, not just code line numbers.
- **Works anywhere:** CLI, notebooks, scripts, web apps, and more.

---


## **🌐 Links**
- [GitHub](https://github.com/ANU-2524/pybugmate)
- PyPI: Coming soon!

---

> PRs, issues, and stars are welcome !...  
> Built with ♥ by ANU-2524.
