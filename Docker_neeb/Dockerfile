FROM williamspanlab/fsl-in-docker:1.0.3

RUN export DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
            apt-utils \
            bzip2 \
            ca-certificates \
            curl \
            locales \
            unzip \
            ant \
    && apt-get clean


 RUN pip install --upgrade pip
 RUN pip install pydicom


RUN apt update
RUN apt install git -y

RUN mkdir /flywheel
RUN mkdir /flywheel/v0
RUN mkdir /flywheel/v0/input/
RUN mkdir /flywheel/v0/output/
RUN mkdir /flywheel/v0/processing/
RUN mkdir /flywheel/v0/output/H2OMaps/
RUN mkdir /flywheel/v0/output/Myelin/
RUN mkdir /flywheel/v0/output/Myelin/MyelinMaps/
RUN mkdir /flywheel/v0/output/T2Star_Fast/
RUN mkdir /flywheel/v0/output/T2Star_Slow/

RUN echo reclone pls

RUN git clone --branch=master https://github.com/ndesaraju/neeb_docker_utils.git /home/neeb_docker_utils

# Make directory for flywheel spec (v0)
ENV FLYWHEEL /flywheel/v0
WORKDIR ${FLYWHEEL}

# Copy executable/manifest to Gear
COPY run.py ${FLYWHEEL}/run.py
COPY run ${FLYWHEEL}/run
COPY manifest.json /flywheel/v0/manifest.json

# Configure entrypoint
RUN chmod a+x /flywheel/v0/run.py
RUN chmod u+rwx /flywheel/v0/run
ENTRYPOINT ["/flywheel/v0/run"]


