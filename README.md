# 🔎 AI Research Pipeline

A multi-agent research assistant built with **LangChain**, **LangGraph**, and **Gemini**, wrapped in a clean **Streamlit** UI.

Give it a topic, and a chain of agents will search the web, read the most relevant source in depth, draft a structured report, and critique its own work — end to end, in one run.

```
   ┌───────────────┐     ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
   │  Search Agent │ ──▶ │  Reader Agent │ ──▶ │ Writer Chain  │ ──▶ │ Critic Chain  │
   │  (Tavily web  │     │  (scrapes the │     │ (drafts the   │     │ (scores &     │
   │   search)     │     │   best URL)   │     │   report)     │     │  reviews it)  │
   └───────────────┘     └───────────────┘     └───────────────┘     └───────────────┘
```

## ✨ Features

- **Search Agent** — queries the web via Tavily and surfaces titles, URLs, and snippets
- **Reader Agent** — picks the most relevant result and scrapes its full text for deeper context
- **Writer Chain** — synthesizes everything into a structured report (Introduction, Key Findings, Conclusion, Sources)
- **Critic Chain** — independently scores the report out of 10 and lists strengths and areas to improve
- **Streamlit UI** — live per-stage progress, tabbed results (Report / Critique / Raw Research), and one-click markdown download

## 🗂️ Project Structure

```
.
├── agents.py          # Agent + chain definitions (search agent, reader agent, writer & critic chains)
├── tools.py           # web_search (Tavily) and scrape_url (requests + BeautifulSoup) tools
├── pipeline.py         # CLI entry point that runs the full 4-stage pipeline
├── streamlit_app.py    # Streamlit front-end for the pipeline
└── .env                # API keys (not committed)
```

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| Orchestration | LangChain, LangGraph (`create_agent`) |
| LLM | Google Gemini (`langchain-google-genai`) |
| Web search | Tavily |
| Scraping | `requests` + `BeautifulSoup` |
| UI | Streamlit |

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

### 2. Set up a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install langchain langchain-community langchain-core langchain-google-genai \
            langgraph tavily-python beautifulsoup4 requests python-dotenv streamlit rich
```

> Tip: once your environment is working, freeze it with `pip freeze > requirements.txt` so future installs are a single `pip install -r requirements.txt`.

### 4. Add your API keys

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

## ▶️ Usage

### Streamlit UI (recommended)

```bash
streamlit run streamlit_app.py
```

Enter a topic, click **Run 🚀**, and watch each stage complete live. Results appear in tabs for the final report, the critique, and the raw search/scrape output, with a markdown download button for the report.

### Command line

```bash
python pipeline.py
```

You'll be prompted for a topic, and the pipeline will print its progress and final output to the console.

## 📋 Example

**Input:** `The impact of AI agents on software engineering jobs`

**Output:**
- A structured Markdown report with an introduction, at least three key findings, a conclusion, and a source list
- A critique with a `Score: X/10`, strengths, areas to improve, and a one-line verdict

## ⚠️ Known Issues

- `web_search` in `tools.py` currently returns after processing only the first search result, because its `return` statement sits inside the `for` loop. Dedent it to after the loop to let the search agent see all returned sources.

## 🗺️ Roadmap

- [ ] Fix `web_search` to return all results
- [ ] Add a `requirements.txt`
- [ ] Support multiple source scraping in the reader agent
- [ ] Export reports as PDF/DOCX
- [ ] Add caching to avoid re-running identical topics

## 📄 License

[MIT](LICENSE) — feel free to use, modify, and share.

## 🤝 Contributing

Issues and pull requests are welcome. If you spot a bug or have an idea for a new stage in the pipeline, open an issue first to discuss what you'd like to change.
