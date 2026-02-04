FROM unit:python3.14-slim

COPY packages.txt requirements.txt bashrc /

# create user
RUN mkdir -p /app \
    && useradd user \
    && mkdir -p /home/user/bin \
    && chown -R user:user /home/user \
    && chmod -R 755 /home/user /app \
    && cat /bashrc >> /home/user/.bashrc \
    && cat /bashrc >> /root/.bashrc

# apt install packages
RUN \
    apt-get update \
    && apt-get install -y --no-install-recommends $(cat /packages.txt)

# pip install packages
RUN pip3 install --upgrade pip setuptools \
    && pip3 install -r /requirements.txt

RUN chown -R user:user /home/user

WORKDIR /app
