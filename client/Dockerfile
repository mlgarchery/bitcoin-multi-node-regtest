FROM ubuntu:18.04

RUN apt-get update && apt-get -y install curl jq

# this can take time
RUN curl -OL https://bitcoin.org/bin/bitcoin-core-22.0/bitcoin-22.0-x86_64-linux-gnu.tar.gz

RUN tar zxvf bitcoin-22.0-x86_64-linux-gnu.tar.gz && cp /bitcoin-22.0/bin/bitcoin-cli /bitcoin-cli

COPY ./bitcoin.conf /root/.bitcoin/bitcoin.conf

RUN echo "rpcport=18400" >> /root/.bitcoin/bitcoin.conf

RUN rm -rf /bitcoin-22.0 bitcoin-22.0-x86_64-linux-gnu.tar.gz

# port to access other node
EXPOSE 18400/tcp
EXPOSE 18401/tcp
EXPOSE 18402/tcp
