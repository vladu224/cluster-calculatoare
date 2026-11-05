FROM python:3.12-slim

WORKDIR /code

COPY libs/auth_client /libs/auth_client
RUN pip install --no-cache-dir /libs/auth_client
COPY services/auth/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/auth/app ./app
CMD [ "watchfiles", "python -m app.main", "app" ]