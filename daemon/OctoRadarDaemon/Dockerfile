FROM python:3.8-slim-buster

WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app/OctoRadarDaemon

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r OctoRadarDaemon/requirements.txt

# Run the application when the container launches
CMD ["python", "-m", "OctoRadarDaemon"]