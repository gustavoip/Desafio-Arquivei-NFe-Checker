FROM python:3.6

COPY requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app
RUN pip install -r requirements.txt
COPY . /opt/app
ENV PYTHONPATH "${PYTHONPATH}:/opt/app/"
EXPOSE 5000 5000
ENTRYPOINT [ "python", "nfe_checker/app.py" ]
