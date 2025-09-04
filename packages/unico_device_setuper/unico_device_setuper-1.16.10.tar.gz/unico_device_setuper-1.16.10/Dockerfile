FROM ghcr.io/astral-sh/uv:0.7.1-debian-slim AS python-base
RUN apt-get update
ENV UV_PYTHON_INSTALL_DIR=/root/python


FROM python-base AS python-dev
RUN apt-get install gcc clang libc-dev libffi-dev --yes


FROM python-dev AS app-builder
WORKDIR /app
COPY .python-version .
COPY pyproject.toml .
COPY uv.lock .
COPY README.md .
COPY src src
ENV CACHE_DIR=/root/.cache
ENV UV_CACHE_DIR=$CACHE_DIR/uv
ENV UV_PYTHON_CACHE_DIR=$CACHE_DIR/uv-python
ENV UV_LINK_MODE=copy
RUN --mount=type=cache,dst=$CACHE_DIR uv sync --no-dev


FROM python-base AS runtime
WORKDIR /app
COPY --from=app-builder $UV_PYTHON_INSTALL_DIR $UV_PYTHON_INSTALL_DIR
COPY --from=app-builder /app/src src
COPY --from=app-builder /app/.venv .venv
COPY config config
ARG CONFIG
ENV DEVICE_SETUPER_CONFIG=$CONFIG
ENV DEVICE_SETUPER_ENV=deployed
RUN touch /app/config.toml
LABEL com.datadoghq.ad.logs="[{\"service\": \"device-setuper\"}]"
ENTRYPOINT [".venv/bin/gunicorn", "--config", "config/gunicorn.py", "unico_device_setuper.backend.app:APP"]
