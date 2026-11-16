FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates wget gnupg socat python3 lsb-release software-properties-common \
    && wget -qO /tmp/llvm.sh https://apt.llvm.org/llvm.sh \
    && chmod +x /tmp/llvm.sh && /tmp/llvm.sh 22 \
    && apt-get update && apt-get install -y --no-install-recommends clang-22 \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /usr/lib/llvm \
    && ln -sfn /usr/lib/llvm-22 /usr/lib/llvm/22
RUN userdel -r ubuntu 2>/dev/null; useradd -m -u 1000 ctf
WORKDIR /opt/chal
COPY compilerIBarelyKnowHer.so /opt/chal/compilerIBarelyKnowHer.so
COPY runtime.o    /opt/chal/runtime.o
COPY dslc         /opt/chal/dslc
COPY handler.sh   /opt/chal/handler.sh
COPY flag.txt     /opt/chal/flag.txt
RUN chmod 0755 /opt/chal/handler.sh /opt/chal/dslc && chmod 0444 /opt/chal/flag.txt
USER ctf
EXPOSE 1337
CMD ["socat", "-T60", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:/opt/chal/handler.sh,stderr"]
