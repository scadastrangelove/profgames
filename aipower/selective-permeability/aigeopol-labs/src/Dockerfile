FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /work

COPY code/ /work/code/
COPY config/ /work/config/
COPY scenarios/ /work/scenarios/
COPY docs/ /work/docs/
COPY README.md /work/README.md

RUN python -m py_compile /work/code/*.py

ENTRYPOINT ["python"]
