FROM python:3.11-slim

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME

# Copy local code to the container image
COPY . .

# Install dependencies
RUN pip install --upgrade pip setuptools
RUN pip install -r requirements.txt

# Run the web service on container startup.
CMD ["inv", "run"]
