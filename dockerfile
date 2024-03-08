ARG MLFLOW_RUN_ID
ARG MLFLOW_TRACKING_URI
ARG MLFLOW_S3_ENDPOINT_URL
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY

FROM python:3.11.2-bullseye as mlflow

ARG MLFLOW_RUN_ID
ARG MLFLOW_TRACKING_URI
ARG MLFLOW_S3_ENDPOINT_URL
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY

ENV MLFLOW_TRACKING_URI="http://mlflow-reykkr-dev.apps.sandbox-m4.g2pi.p1.openshiftapps.com/"
ENV MLFLOW_S3_ENDPOINT_URL="http://minio-console-reykkr-dev.apps.sandbox-m4.g2pi.p1.openshiftapps.com/"
ENV AWS_ACCESS_KEY_ID="minio"
ENV AWS_SECRET_ACCESS_KEY="minio123"

ENV APP_ROOT=/opt/app-root

WORKDIR ${APP_ROOT}

COPY --chown=${USER} cats_dogs_other/api ./cats_dogs_other/api

RUN pip install mlflow[extras]

RUN mlflow artifacts download -u runs:/b5e069c28b1b47468bb6ca3006ce9ead/artifacts/model/data/model.h5 -d ./cats_dogs_other/api/resources

FROM python:3.11.2-bullseye as runtime

ENV APP_ROOT=/opt/app-root

WORKDIR ${APP_ROOT}

COPY --chown=${USER} boot.py ./boot.py
COPY --chown=${USER} packages ./packages
COPY --chown=${USER} init_packages.sh ./init_packages.sh
COPY --chown=${USER} --from=mlflow ${APP_ROOT}/cats_dogs_other/api ./cats_dogs_other/api

RUN chmod 777 ./init_packages.sh
RUN ./init_packages.sh
RUN pip install -r ./cats_dogs_other/api/requirements.txt

EXPOSE 8080

ENTRYPOINT ["python3", "boot.py"]