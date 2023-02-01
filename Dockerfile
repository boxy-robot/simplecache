FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1

# COPY requirements-to-freeze.txt /app/requirements-to-freeze.txt
# RUN pip3 install -r /app/requirements-to-freeze.txt

COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-deps -r /app/requirements.txt

WORKDIR /app
COPY . .

CMD ["bash"]
