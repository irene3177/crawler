# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libdbus-1-3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxss1 \
    libasound2 \
    libatk1.0-0 \
    libcups2 \
    libgtk-3-0 \
    libgbm1 \
    libpango1.0-0 \
    libcairo2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file (if you have one) and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .
# Install Playwright and its browsers
RUN pip install playwright
RUN playwright install
# Expose port if your app serves HTTP requests (optional)
# EXPOSE 80

# Define the command to run your application
# Copy the entrypoint script into the container
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

# Define the entrypoint to allow passing parameters
ENTRYPOINT ["./entrypoint.sh"]