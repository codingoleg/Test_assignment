FROM python:3.10

COPY . /Test_assignment
WORKDIR /Test_assignment
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

CMD [ "python", "run.py" ]