FROM nginx/unit:1.29.0-python3.11

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

# install pnpm
RUN wget -qO- https://get.pnpm.io/install.sh | ENV="/home/user/.bashrc" SHELL="$(which bash)" bash - \
&& mkdir -p /home/user/.local/share \
&& cp -r /root/.local/share/pnpm /home/user/.local/share/

# pip install packages
RUN pip3 install --upgrade pip setuptools \
    && pip3 install -r /requirements.txt

RUN chown -R user:user /home/user

WORKDIR /app
