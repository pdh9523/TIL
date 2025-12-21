FROM python:3.12-slim

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONUNBUFFERED=1

ARG REQUIREMENT='requirements.txt'

COPY $REQUIREMENT /tmp/
RUN pip install --no-cache-dir -r /tmp/$REQUIREMENT

ENV PYTHONUNBUFFERED 1

WORKDIR /app
EXPOSE 8000
CMD ["python" "app.py"]