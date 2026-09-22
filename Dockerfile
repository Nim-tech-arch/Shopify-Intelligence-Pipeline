# 1. Base Image
FROM python:3.11-slim

# 2. Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 3. Set working directory inside the container
WORKDIR /app

# 4. Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt-get/lists/*

# 5. Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the entire repository code into the container
COPY . .

# 7. Expose Render's standard port
EXPOSE 10000

# 8. Start FastAPI / Uvicorn server
CMD ["uvicorn", "Serving_Shopify_Merchants.Merchants_serving:app", "--host", "0.0.0.0", "--port", "10000"]