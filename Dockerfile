FROM python:3.11-alpine AS base

ARG APP_USER=pg-crud

RUN adduser -D -u 1000 ${APP_USER} && \
    apk --no-cache add curl gcc python3-dev py3-setuptools musl-dev && \
    pip install pdm

ENV PATH="/root/.local/bin:${PATH}"

FROM base AS prod

ENV APP_DIR=/pg-crud
WORKDIR ${APP_DIR}

COPY src pdm.lock pyproject.toml ${APP_DIR}

RUN pdm install --prod --no-self
RUN chown -R ${APP_USER}:${APP_USER} ${APP_DIR}

CMD pdm run ${APP_DIR}/main.py

USER ${APP_USER}
