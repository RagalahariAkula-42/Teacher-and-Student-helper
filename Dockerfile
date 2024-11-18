# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Install necessary system dependencies
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    awscli \
    libgtk2.0-dev \
    libboost-python1.67-dev \
    libboost-system1.67-dev \
    libboost-thread1.67-dev \
    libopenblas-dev \
    liblapack-dev \
    gfortran \
    libgl1-mesa-glx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Upgrade pip and install required Python packages
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt


# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python3", "app.py"]
