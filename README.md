# 🧬 Pulse - Module Extraction AI Agent

A "Next Level" AI-powered tool that extracts structured information (modules and submodules) from documentation websites. Built with Streamlit, FastAPI, and OpenAI.

## 🚀 Features

- **Advanced Crawling**: Recursively crawls multiple documentation URLs.
- **AI Extraction**: Uses OpenAI's GPT-4o to identify modules, submodules, and descriptions with high precision.
- **Strict JSON Output**: Guarantees the output format required for downstream integration.
- **Interactive Visualization**: Generates dynamic hierarchy graphs.
- **Dual Interface**: 
  - **Web UI**: Modern Streamlit dashboard.
  - **REST API**: FastAPI endpoint for programmatic access.
- **Caching**: Implements caching to avoid redundant API calls.
- **Confidence Scores**: Provides AI confidence levels for extracted data.

## 🛠️ Setup

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd pulse_module_extractor
   ```

2. **Environment Setup:**
   Create a `.env` file in the root directory:
   ```bash
   OPENAI_API_KEY=your_api_key_here
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application:**
   ```bash
   streamlit run app.py
   ```

5. **Run the API (Optional):**
   ```bash
   uvicorn api:app --reload
   ```

## 🐳 Docker

Build and run the container (runs both UI and API):

```bash
docker build -t pulse-extractor .
docker run -p 8501:8501 -p 8000:8000 --env-file .env pulse-extractor
```

- **UI**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

## � CLI Usage

You can run the extractor directly from the command line:

```bash
# Basic usage
python module_extractor.py --urls https://help.instagram.com

# Advanced usage
python module_extractor.py --urls https://help.instagram.com https://support.stripe.com --depth 2 --output my_report.json
```

## �📡 API Usage

**Endpoint:** `POST /extract`

**Request:**
```json
{
  "urls": ["https://help.instagram.com"],
  "max_depth": 1
}
```

**Response:**
```json
{
  "modules": [
    {
      "module": "Account Settings",
      "Description": "...",
      "Submodules": { ... },
      "confidence_score": 0.95
    }
  ],
  "pages_crawled": 5
}
```

## 🧪 Testing

Run the test suite:
```bash
pytest
```
