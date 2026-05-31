FROM python:3.11-slim
WORKDIR /app
COPY flask/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY flask/ .
EXPOSE 7860
ENV PORT=7860
CMD ["python", "main.py"]
