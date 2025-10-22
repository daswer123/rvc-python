FROM python:3.10-slim

RUN apt-get update -y && \
    apt-get install -y default-libmysqlclient-dev pkg-config gcc g++ libgl1 libglib2.0-0

COPY . /code

WORKDIR /code

RUN pip install -r requirements.txt

RUN pip install --pre torch torchaudio --index-url https://download.pytorch.org/whl/nightly/cu126

ENV TORCH_CUDA_ARCH_LIST="5.0;6.0;7.0;7.5;8.0;8.6;9.0;12.0"

ENV PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
