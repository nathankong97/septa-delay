# Use official Python image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /septa-delay

# Install cron
RUN apt-get update && apt-get install -y cron sqlite3 python3-pip tzdata

# Set the timezone to Philadelphia (America/New_York)
ENV TZ=America/New_York
RUN ln -sf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Ensure `python` command is available
RUN ln -s /usr/local/bin/python3 /usr/bin/python

# Copy project files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose logs directory
VOLUME ["/septa-delay/logs"]

# Set the entrypoint script
CMD ["bash", "/septa-delay/run_scraper.sh"]
