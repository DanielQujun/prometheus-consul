FROM python:3.9.7-buster

WORKDIR /consulProme

RUN apt-get update && apt-get install -y vim && apt-get clean all && rm -rf /var/lib/apt/*

RUN pip install requests pyyaml absl-py -i https://pypi.tuna.tsinghua.edu.cn/simple

ADD . /consulProme/

RUN ln -s /consulProme/kubectl /usr/bin/

ENTRYPOINT ["python3", "main.py"]
