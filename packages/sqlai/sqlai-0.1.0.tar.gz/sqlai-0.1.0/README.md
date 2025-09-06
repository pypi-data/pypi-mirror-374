# SQLAI

**SQLAI** is a command-line tool that uses generative AI (Google Gemini, OpenAI, etc.) to help you interact with SQL queries. It can explain, validate, and (soon) improve SQL queries, leveraging the power of modern AI models.

---

## Features

- **Explain** Explains in plain English what SQL query does.
- **Validate** check for general correctness.
- **Improve** (coming soon): Suggest improvements to your SQL queries.
- **Configurable**: Choose your AI provider, API key, and model.
- **Simple CLI**: Easy-to-use command-line interface.

---

## Local Development

To set up your development environment and use the CLI tool while working on the project:

### 1. Clone the repository

```bash
git clone https://github.com/alexanderbrueck/sqlai.git
cd sqlai
```

### 2. Install in editable mode

From the project root, run:

```bash
pip install -e .
```

- The `-e .` flag installs your package in "editable" mode, so changes to the code are immediately reflected without reinstalling.
- All required dependencies will be installed automatically, as they are specified in `setup.py` (`install_requires`).  
- **You do not need to run `pip install -r requirements.txt` separately.**

---

## Quick Start

1. **Configure your AI provider and credentials:**

   ```bash
   sqlai set_config
   ```

   You’ll be prompted for:
   - AI provider (e.g., `gemini`, `openai`)
   - API key
   - Model name (e.g., `gemini-1.5-flash`)

2. **Analyze a SQL file:**

   ```bash
   sqlai run path/to/your_query.sql
   ```

   You will be shown several actions (explain, validate, ...), and you can select one interactively.

3. **Show your current configuration:**

   ```bash
   sqlai show_config
   ```

---

## Example Usage

```bash
sqlai set_config
sqlai run my_query.sql
```

---

## Requirements

- Python 3.7+
- [google-generativeai](https://pypi.org/project/google-generativeai/)
- [tomli](https://pypi.org/project/tomli/)
- [tomli-w](https://pypi.org/project/tomli-w/)

Install all dependencies via:

```bash
pip install -r requirements.txt
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Notes

- Only `.sql` files are supported for analysis.
- The "improve" feature is coming soon.
- Your credentials are stored in `~/.sqlai/config.toml`.

---

## Contributing

Pull requests and feedback are welcome! Please open an issue or PR to discuss changes or suggestions.