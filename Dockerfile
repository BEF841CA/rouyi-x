FROM python:alpine
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
ENV HOST=0.0.0.0
ENV PORT=8000
EXPOSE $PORT
CMD uvicorn app.application:application --host $HOST --port $PORT