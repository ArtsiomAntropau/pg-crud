FROM python:3.11-alpine AS base

COPY src ./
COPY pdm.lock pyproject.toml ./

RUN apk add curl gcc python3-dev musl-dev
RUN curl -sSL https://pdm.fming.dev/dev/install-pdm.py | python3 -

ENV PATH="/root/.local/bin:${PATH}"

FROM base AS prod

RUN pdm install --prod

CMD pdm run src/main.py
