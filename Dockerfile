# Build用コンテナ
FROM python:3.11.4-bookworm as builder

WORKDIR /opt/app
COPY requirements.txt /opt/app
RUN pip3 install -r requirements.txt

#　実行用コンテナ
FROM python:3.11.4-slim-bookworm as runner

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/streamlit /usr/local/bin/streamlit

RUN apt update \
  && apt-get install -y fonts-ipafont \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app
COPY main /opt/app/main

EXPOSE 8080

ENV PYTHONPATH /opt/app/main

CMD cd $PYTHONPATH; streamlit run ./main/dashboard_main.py \
    --browser.serverAddress="0.0.0.0" \
    --server.port="8080"

