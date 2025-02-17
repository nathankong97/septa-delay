# Use official Python image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /septa-delay

# Copy project files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose logs directory (Optional)
VOLUME ["/septa-delay/logs"]

# Set the entrypoint script
CMD ["bash", "/septa-delay/run_scraper.sh"]
