########################################################################
# Build the application image                                          #
########################################################################

# Use an official Python runtime as a parent image
FROM python:3.9 as app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV MEDIA_ROOT /hummus/media/
ENV SERVE_MEDIA false
ENV MEDIA_X_ACCEL_REDIRECT_URL /media-redirect/

# Install dependencies
RUN pip install --upgrade pip
RUN pip install pipenv

# Install application
COPY Pipfile Pipfile.lock /hummus/app/
WORKDIR /hummus/app/
RUN pipenv install --system --deploy
COPY . /hummus/app/

# Configure media volume
RUN mkdir /hummus/media/ && chown www-data:www-data /hummus/media/
VOLUME /hummus/media/

EXPOSE 8000
CMD exec gunicorn hummus.wsgi -u www-data -g www-data \
		--bind [::]:8000 --workers 4 --log-file -


########################################################################
# Build the nginx image to serve static files and media                #
########################################################################

FROM app as staticfiles
RUN ./manage.py collectstatic --no-input

FROM nginx:latest as nginx
COPY --from=staticfiles /hummus/app/staticfiles /usr/share/nginx/html/static
COPY deploy/dev/nginx.conf /etc/nginx/conf.d/default.conf
VOLUME /usr/share/nginx/html/media-redirect
