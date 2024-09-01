FROM ubuntu:22.04
RUN apt-get update && apt-get install -y netcat
ENV PORT=12345
ENV MESSAGE="Hello world"
CMD ["bash", "-c", "echo ${MESSAGE} | nc server ${PORT}"]