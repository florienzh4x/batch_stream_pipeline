ARG SPARK_VERSION

FROM apache/spark:${SPARK_VERSION:-3.5.5-debian-12-r3}

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    wget \
    htop \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER spark

# download jar

ARG HADOOP_AWS_JAR_VERSION
ARG MINIO_JAR_VERSION
ARG POSTGRESQL_JAR_VERSION
ARG AWS_BUNDLE_JAR_VERSION
ARG JARS_DIRECTORY

RUN wget --no-check-certificate "https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/$HADOOP_AWS_JAR_VERSION/hadoop-aws-$HADOOP_AWS_JAR_VERSION.jar" -O $JARS_DIRECTORY/hadoop-aws-$HADOOP_AWS_JAR_VERSION.jar
RUN wget --no-check-certificate "https://repo1.maven.org/maven2/io/minio/minio/$MINIO_JAR_VERSION/minio-$MINIO_JAR_VERSION-all.jar" -O $JARS_DIRECTORY/minio-$MINIO_JAR_VERSION-all.jar
RUN wget --no-check-certificate "https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/$AWS_BUNDLE_JAR_VERSION/aws-java-sdk-bundle-$AWS_BUNDLE_JAR_VERSION.jar" -O $JARS_DIRECTORY/aws-java-sdk-bundle-$AWS_BUNDLE_JAR_VERSION.jar
RUN wget --no-check-certificate "https://repo1.maven.org/maven2/org/postgresql/postgresql/$POSTGRESQL_JAR_VERSION/postgresql-$POSTGRESQL_JAR_VERSION.jar" -O $JARS_DIRECTORY/postgresql-$POSTGRESQL_JAR_VERSION.jar

RUN chmod -R 777 $JARS_DIRECTORY