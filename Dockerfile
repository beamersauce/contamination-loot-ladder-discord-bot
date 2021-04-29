FROM python:3.7.5-slim
WORKDIR /app
RUN python -m pip install \
        discord \
        google-api-python-client google-auth-httplib2 google-auth-oauthlib

COPY . /app
ENTRYPOINT ["python", "-u", "/app/src/main.py"]

#TODO copy over code (create a release?) https://packaging.python.org/tutorials/packaging-projects/
#TODO auto run code
#TODO need to autoloadload/mnt sheets and discord secrets if we have a release