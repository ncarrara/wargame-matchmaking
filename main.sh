#!/bin/bash
set -e
source .env

# Start Flask in background
echo "Starting Flask..."
poetry run python upload_server.py &

# Start Streamlit in background
echo "Starting Streamlit..."
poetry run streamlit run app.py --server.port=3000 --server.address=0.0.0.0 &

# Wait for all background processes to finish
wait
