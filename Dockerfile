FROM python:3.11

# declare app directory
WORKDIR /app

# copy python code
COPY config.py .
COPY runner.py .
COPY logger.py .
COPY requirements.txt .

# install dependencies
RUN pip3.11 install -r requirements.txt

# start server
ENTRYPOINT ["python3.11"]
CMD ["runner.py"]
