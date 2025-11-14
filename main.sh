#!/bin/bash
set -e

# Start Flask in background
echo "Starting Flask..."
poetry run python upload_server.py &

# Start Streamlit in background
echo "Starting Streamlit..."
poetry run streamlit run app.py --server.port=8501 --server.address=0.0.0.0 &

# Wait for all background processes to finish
wait
