FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for graphviz
RUN apt-get update && apt-get install -y graphviz && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose ports for Streamlit (8501) and FastAPI (8000)
EXPOSE 8501 8000

# Create a script to run both
RUN echo '#!/bin/bash\nstreamlit run app.py --server.address=0.0.0.0 & uvicorn api:app --host 0.0.0.0 --port 8000' > start.sh
RUN chmod +x start.sh

CMD ["./start.sh"]
