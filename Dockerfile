FROM debian:buster

WORKDIR /opt/wofs

ARG INDEX_URL
ENV PIP_EXTRA_INDEX_URL=$INDEX_URL

ARG WofsPackageVersion
ENV WOFS_VERSION=$WofsPackageVersion

ENV CNDA=/opt/miniconda

ENV PATH="${CNDA}/bin:${PATH}"

ENV PROJ_LIB="${CNDA}/share/proj" 

RUN apt update && apt install -y curl unzip

# RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O conda-install.sh && \
#     chmod 755 conda-install.sh && \
#     sh conda-install.sh -b -p $CNDA && \
#     rm -f conda-install.sh && \
#     echo $PATH && \
#     conda init bash

COPY ./wofs_satellite /opt/wofs/wofs_satellite
COPY ./environment.yml /opt/wofs

RUN curl micro.mamba.pm/install.sh | bash && \
    #micromamba shell activate && \
    /root/.local/bin/micromamba env create --file /opt/wofs/environment.yml && \
    micromamba activate wofs-satellite && \
    echo "micromamba activate wofs-satellite" >> ~/.bashrc

# override the RUN command to use --login, which will load profile scripts (bashrc) and make conda visible
SHELL ["/bin/bash", "--login", "-c"]

# RUN conda env create --file /opt/wofs/environment.yml 

WORKDIR /opt/wofs/wofs_satellite

ENTRYPOINT ["bash", "create.sh"]
