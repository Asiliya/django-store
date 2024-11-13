# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container to /app
WORKDIR /app

COPY requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip \
  && pip install -r /app/requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Ensure the entrypoint script is executable
RUN chmod a+x /app/store/entrypoint.sh

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the application
CMD ["sh", "store/entrypoint.sh"]