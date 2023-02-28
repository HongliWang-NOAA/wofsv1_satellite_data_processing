FROM debian:buster

WORKDIR /opt/wofs

ARG INDEX_URL
ENV PIP_EXTRA_INDEX_URL=$INDEX_URL

ARG WofsPackageVersion
ENV WOFS_VERSION=$WofsPackageVersion

ENV CNDA=/opt/miniconda

ENV PATH="${CNDA}/bin:${PATH}"

ENV PROJ_LIB="${CNDA}/share/proj" 

RUN apt update && apt install -y curl unzip bzip2

COPY ./wofs_satellite /opt/wofs/wofs_satellite
COPY ./environment.yml /opt/wofs

RUN curl micro.mamba.pm/install.sh | bash && \
    /root/.local/bin/micromamba env create --file /opt/wofs/environment.yml && \
    echo "micromamba activate wofs-satellite" >> ~/.bashrc 

# override the RUN command to use --login, which will load profile scripts (bashrc) and make conda visible
SHELL ["/bin/bash", "--login", "-c"]

RUN micromamba activate wofs-satellite && \  
    python -m pip install wofs==$WofsPackageVersion

WORKDIR /opt/wofs/wofs_satellite

ENTRYPOINT ["bash", "create.sh"]
