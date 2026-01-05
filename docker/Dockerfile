FROM alpine/git AS init
WORKDIR /mcrcon-bot 
RUN git clone -b main https://github.com/Rhubaruth/mcron-bot.git .
RUN git fetch && git pull

FROM python:3.13-slim
WORKDIR /app
COPY --from=init /mcrcon-bot .
RUN pip install -r requirements.txt
CMD ["python", "./main.py"]
