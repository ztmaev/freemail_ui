# Use official Python image
FROM python:3.11

# Set working directory inside the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Expose port 5000
EXPOSE 5000

# Run the Flask app
CMD ["sh", "-c", "python db_create.py && python app.py"]
