ARG TRINO_VERSION

FROM trinodb/trino:${TRINO_VERSION:-474}

USER root

ARG KEYSTORE_FILE
ARG KEYSTORE_PASSWORD

RUN keytool -genkeypair \
    -alias trino \
    -keyalg RSA \
    -keysize 2048 \
    -keystore $KEYSTORE_FILE \
    -validity 3650 \
    -storepass $KEYSTORE_PASSWORD \
    -dname "CN=trino, OU=IT, O=Company, L=City, S=State, C=ID"

# download jar

ARG HADOOP_AWS_JAR_VERSION
ARG MINIO_JAR_VERSION
ARG POSTGRESQL_JAR_VERSION
ARG AWS_BUNDLE_JAR_VERSION
ARG JARS_DIRECTORY

RUN curl -skL "https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/$HADOOP_AWS_JAR_VERSION/hadoop-aws-$HADOOP_AWS_JAR_VERSION.jar" -o $JARS_DIRECTORY/hadoop-aws-$HADOOP_AWS_JAR_VERSION.jar
RUN curl -skL "https://repo1.maven.org/maven2/io/minio/minio/$MINIO_JAR_VERSION/minio-$MINIO_JAR_VERSION.jar" -o $JARS_DIRECTORY/minio-$MINIO_JAR_VERSION.jar
RUN curl -skL "https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/$AWS_BUNDLE_JAR_VERSION/aws-java-sdk-bundle-$AWS_BUNDLE_JAR_VERSION.jar" -o $JARS_DIRECTORY/aws-java-sdk-bundle-$AWS_BUNDLE_JAR_VERSION.jar
RUN curl -skL "https://repo1.maven.org/maven2/org/postgresql/postgresql/$POSTGRESQL_JAR_VERSION/postgresql-$POSTGRESQL_JAR_VERSION.jar" -o $JARS_DIRECTORY/postgresql-$POSTGRESQL_JAR_VERSION.jar

RUN chmod 755 $JARS_DIRECTORY/*.jar
RUN chown trino:trino $JARS_DIRECTORY/*.jar

USER trino