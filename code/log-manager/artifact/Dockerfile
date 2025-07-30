# Use an official Python runtime as a parent image
FROM python:3.11

# Install any needed packages specified in requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Run main.py when the container launches
CMD ["python", "app.py"]
