FROM python:3-onbuild

# Copying source in current directory into the image
# python:3-onbuild expects the source in /usr/src/app
COPY . /usr/src/app

#ADD . /usr/src/app
#WORKDIR . /usr/src/app
#RUN pip3 install -r requirements.txt

# Commands in a list
CMD ["python", "api.py"]
