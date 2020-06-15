FROM python:3.6

# declare app directory
WORKDIR /app

# copy python code
COPY config.py .
COPY runner.py .
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# start server
ENTRYPOINT ["python3"]
CMD ["runner.py"]
