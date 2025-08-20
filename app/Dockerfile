FROM python:3.11-slim

WORKDIR /app

COPY app.py /app/app.py

RUN pip install dash plotly

EXPOSE 8050

CMD ["python", "app.py"]