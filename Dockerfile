# Use Playwright official Python image (includes browser dependencies)
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps

CMD ["python", "main.py"]
