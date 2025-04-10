FROM debian:bookworm-slim

WORKDIR /opt/wofs

ARG INDEX_URL
ENV PIP_EXTRA_INDEX_URL=$INDEX_URL

ENV CNDA=/opt/miniconda

ENV PATH="${CNDA}/bin:${PATH}"

ENV PROJ_LIB="${CNDA}/share/proj" 

ENV MAMBA_ROOT_PREFIX=/opt/micromamba

RUN apt update && apt install -y curl unzip bzip2 wget pngquant gcc

COPY ./wofs_satellite /opt/wofs/wofs_satellite
COPY ./environment.yml /opt/wofs

RUN curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj bin/micromamba

# RUN /opt/wofs/bin/micromamba shell hook -s posix > /opt/load.sh && \
#     . /opt/load.sh && \
#     /opt/wofs/bin/micromamba env create --file /opt/wofs/environment.yml && \
#     echo ". /opt/load.sh && micromamba activate wofs-satellite" >> ~/.bashrc && \
#     micromamba activate wofs-satellite

# override the RUN command to use --login, which will load profile scripts (bashrc) and make conda visible
SHELL ["/bin/bash", "--login", "-c"]

RUN mkdir -p ~/miniconda3 && \
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh && \
    bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3 && \
    rm ~/miniconda3/miniconda.sh && \
    echo "source ~/miniconda3/bin/activate && conda activate wofs-satellite" >> ~/.bashrc && \
    source ~/miniconda3/bin/activate && \
    conda env create --file /opt/wofs/environment.yml && \
    source ~/.bashrc

WORKDIR /opt/wofs/wofs_satellite

ENTRYPOINT ["bash", "--login", "source ~/miniconda3/bin/activate && conda activate wofs-satellite && source create.sh"]
