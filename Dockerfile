FROM python:3.12-slim

# Install system dependencies.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
 && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container.
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Upgrade pip and install Python dependencies.
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the repository into the container.
COPY . .

# Expose the port for Streamlit.
EXPOSE 8501

# Set environment variables for headless mode.
ENV STREAMLIT_SERVER_HEADLESS true
ENV STREAMLIT_SERVER_PORT 8501

# Set the default command to run the Streamlit app.
CMD ["streamlit", "run", "src/streamlit_app.py", "--server.enableCORS", "false"]
