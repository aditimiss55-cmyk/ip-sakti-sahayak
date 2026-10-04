FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py corpus.py corpus_hi.py i18n.py eval.py ./
COPY static ./static
ENV HOST=0.0.0.0 PORT=8000 IPSAKTI_DB=/data/ipsakti.db
RUN mkdir -p /data
EXPOSE 8000
CMD ["python", "app.py"]
