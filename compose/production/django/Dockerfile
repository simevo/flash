ARG APP_BASE_IMAGE=deps-backend-base

# define an alias for the specific python version used in this file.
FROM docker.io/python:3.12.10-slim-bookworm AS python

# Python build stage
FROM python as deps-backend-base

ARG APP_HOME=/app
ARG BUILD_ENVIRONMENT=production

WORKDIR ${APP_HOME}

# Install apt packages
RUN apt-get update && apt-get install --no-install-recommends -y \
  # dependencies for building Python packages
  build-essential \
  # psycopg dependencies
  libpq-dev

# Requirements are installed here to ensure they will be cached.
COPY ./requirements .

# Create Python Dependency and Sub-Dependency Wheels.
RUN pip wheel --wheel-dir /usr/src/app/wheels  \
  -r ${BUILD_ENVIRONMENT}.txt


FROM ${APP_BASE_IMAGE} AS backend-base

# Python 'run' stage
FROM python as backend

ARG BUILD_ENVIRONMENT=production
ARG APP_HOME=/app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV BUILD_ENV=${BUILD_ENVIRONMENT}

WORKDIR ${APP_HOME}

RUN addgroup --system django \
    && adduser --system --ingroup django django


# Install required system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
  # psycopg dependencies
  libpq-dev \
  # Translations dependencies
  gettext \
  # entrypoint
  wait-for-it \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# All absolute dir copies ignore workdir instruction. All relative dir copies are wrt to the workdir instruction
# copy python dependency wheels from backend-base
COPY --from=backend-base /usr/src/app/wheels  /wheels/

# use wheels to install python dependencies
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
  && rm -rf /wheels/


COPY --chown=django:django ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint && \
    chmod +x /entrypoint


COPY --chown=django:django ./compose/production/django/start /start
RUN sed -i 's/\r$//g' /start && \
    chmod +x /start
COPY --chown=django:django ./compose/production/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker && \
    chmod +x /start-celeryworker


COPY --chown=django:django ./compose/production/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat && \
    chmod +x /start-celerybeat


COPY --chown=django:django ./compose/production/django/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower && \
    chmod +x /start-flower


# copy application code to WORKDIR
COPY --chown=django:django config/ ${APP_HOME}/config/
COPY --chown=django:django docs/ ${APP_HOME}/docs/
COPY --chown=django:django flash/ ${APP_HOME}/flash/
COPY --chown=django:django locale/ ${APP_HOME}/locale/
COPY --chown=django:django news/ ${APP_HOME}/news/
COPY --chown=django:django tests/ ${APP_HOME}/tests/
COPY --chown=django:django \
  justfile \
  load_models.py \
  manage.py \
  merge_production_dotenvs_in_dotenv.py \
  poller.py \
  pyproject.toml \
  ${APP_HOME}/

# make django owner of the WORKDIR directory as well.
RUN chown -R django:django ${APP_HOME}

USER django

RUN DATABASE_URL="" \
  DJANGO_SETTINGS_MODULE="config.settings.test" \
  python manage.py compilemessages

ENTRYPOINT ["/entrypoint"]
