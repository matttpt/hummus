# Use an official Python runtime as a parent image
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN pip install --upgrade pip
RUN pip install pipenv

# Install application
COPY Pipfile Pipfile.lock /app/
WORKDIR /app
RUN pipenv install --system --deploy
COPY . /app
RUN ./manage.py collectstatic --no-input

EXPOSE 8000
CMD exec gunicorn hummus.wsgi -u www-data -g www-data \
		--bind [::]:8000 --workers 4 --log-file -
