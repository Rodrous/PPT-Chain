FROM python:3
WORKDIR "/app"
COPY requirements.txt ./
RUN pip install -r requirements.txt --no-cache-dir

COPY . .
CMD ["uvicorn", "server:app", "--host","0.0.0.0"]