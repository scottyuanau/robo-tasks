FROM python:3.12
# Or any preferred Python version.
ADD robo-tasks.py .
RUN pip install pillow schedule datetime openpyxl requests pandas google-api-python-client google-auth-httplib2 google-auth-oauthlib
CMD ["python", "./robo-tasks.py"]
# Or enter the name of your unique directory and parameter set.