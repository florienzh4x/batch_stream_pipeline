ARG AIRFLOW_IMAGE_VERSION
ARG PYTHON_VERSION


FROM apache/airflow:$AIRFLOW_IMAGE_VERSION-python$PYTHON_VERSION

USER root

ARG JAVA_VERSION

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         openjdk-$JAVA_VERSION-jre-headless \
         procps \
         wget \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

  
ARG HADOOP_AWS_JAR_VERSION
ARG MINIO_JAR_VERSION
ARG POSTGRESQL_JAR_VERSION
ARG AWS_BUNDLE_JAR_VERSION
ARG JARS_DIRECTORY

RUN mkdir -p $JARS_DIRECTORY

RUN wget --no-check-certificate "https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/$HADOOP_AWS_JAR_VERSION/hadoop-aws-$HADOOP_AWS_JAR_VERSION.jar" -O $JARS_DIRECTORY/hadoop-aws-$HADOOP_AWS_JAR_VERSION.jar
RUN wget --no-check-certificate "https://repo1.maven.org/maven2/io/minio/minio/$MINIO_JAR_VERSION/minio-$MINIO_JAR_VERSION-all.jar" -O $JARS_DIRECTORY/minio-$MINIO_JAR_VERSION-all.jar
RUN wget --no-check-certificate "https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/$AWS_BUNDLE_JAR_VERSION/aws-java-sdk-bundle-$AWS_BUNDLE_JAR_VERSION.jar" -O $JARS_DIRECTORY/aws-java-sdk-bundle-$AWS_BUNDLE_JAR_VERSION.jar
RUN wget --no-check-certificate "https://repo1.maven.org/maven2/org/postgresql/postgresql/$POSTGRESQL_JAR_VERSION/postgresql-$POSTGRESQL_JAR_VERSION.jar" -O $JARS_DIRECTORY/postgresql-$POSTGRESQL_JAR_VERSION.jar

RUN chmod -R 777 $JARS_DIRECTORY

COPY --chown=airflow:airflow requirements.txt .

USER airflow

RUN pip install -r requirements.txt

ENV JAVA_HOME=/usr/lib/jvm/java-$JAVA_VERSION-openjdk-amd64
