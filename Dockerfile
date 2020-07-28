FROM python:3.7

RUN pip install imageio==1.5
RUN pip install numpy
RUN pip install Pillow
RUN pip install Flask 

COPY . .

EXPOSE 80

CMD ["python", "server.py"]