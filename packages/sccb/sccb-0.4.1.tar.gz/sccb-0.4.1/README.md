📋 SCCB – Shortcut Clipboard + Command Binder

SCCB is a customizable CLI tool that lets you save and run command shortcuts and clipboard snippets.
It’s like a mix of a snippet manager, alias system, and Git helper, but fully configurable via a JSON file.

I built this project to save time in my daily workflow — instead of typing long Git commands or reusing the same text snippets, I can now run them instantly with sccb.

---

✨ Features

- 🔖 Snippets → Save reusable text (like API keys, tokens, boilerplate) and copy it to your clipboard with one command.
- ⚡ Commands → Save shell command macros and run them instantly.
- 📝 Variable substitution → Use placeholders like {msg} or {key} and fill them at runtime.
- 🛠 Defaults → Define default values for variables in your config or via sccb default.
- 📂 Config file → All shortcuts are stored in ~/.sccb.json (easy to edit, share, or sync).
- 🎨 Pretty output → Uses Rich for nice tables.
- 🖥 Shell integration → Optionally push commands into your shell buffer (zsh).
- 🧹 Simple management → Add, remove, list, set defaults, and edit shortcuts easily.

---

📦 Installation

From PyPI (recommended)

    pip install sccb

From source

    git clone https://github.com/Jinkuman/sccb.git
    cd sccb
    pip install -e .

---

🚀 Usage

Add a Command

    sccb add gitall:"git add . && git commit -m '{msg}' && git push"

- {msg} is a variable placeholder.

- Run it with a custom message:

      sccb run gitall msg:"Initial commit" !

→ Executes git add . && git commit -m 'Initial commit' && git push

- Or define a default:

      sccb default gitall msg:"quick commit"
      sccb run gitall !

→ Executes with "quick commit" as the default message.

---

Add a Snippet (API Key Example)

    sccb add@ apikey:"sk-1234567890abcdef"

- Copy it to clipboard:

      sccb run apikey

→ Copies sk-1234567890abcdef to clipboard.

- With a variable (e.g., different environments):

      sccb add@ apikey:"{env}_sk-1234567890abcdef"
      sccb run apikey env:"dev"

→ Copies dev_sk-1234567890abcdef to clipboard.

- With a default:

      sccb default apikey env:"prod"
      sccb run apikey

→ Copies prod_sk-1234567890abcdef to clipboard.

---

List Shortcuts

    sccb ls

---

Remove a Shortcut

    sccb rm apikey

---

Edit Config

    sccb edit

---

Help

    sccb help

---

Shell Integration (Optional)

You can install shell integration to push commands into your shell buffer (zsh only for now):

    sccb install_shell
    source ~/.zshrc

Then you can type:

    sccb run gitall

and the command will appear in your terminal buffer, ready to run.

---

📌 Example Config (~/.sccb.json)

    {
      "commands": {
        "gitall": {
          "type": "command",
          "value": "git add . && git commit -m '{msg}' && git push",
          "defaults": { "msg": "quick commit" }
        }
      },
      "snippets": {
        "apikey": {
          "type": "snippet",
          "value": "sk-1234567890abcdef",
          "defaults": {}
        }
      }
    }

---

🛠 How I Built It

- Language: Python
- CLI Framework: Typer
- Clipboard: Pyperclip
- Pretty Output: Rich
- Config: JSON file stored at ~/.sccb.json
- Packaging: pyproject.toml + published to PyPI
  This project started as a way to save time typing repetitive Git commands and reusing text snippets. Over time, I added:

- Variable substitution ({msg}, {env})
- Defaults (sccb default)
- Shell integration for buffer mode
- A polished CLI with ls, rm, edit, and help
