# CICD2 · 공지·자료실 WAR → Tomcat 10.1 이미지 (ECR: notice:<커밋 SHA 7자리>)
# 빌드: docker build -f cicd/docker/Dockerfile --build-arg GIT_COMMIT=$(git rev-parse HEAD) -t notice:$(git rev-parse --short HEAD) .
# 비밀값(CHECK_TOKEN, ADMIN_PASSWORD, DB_PASSWORD)은 이미지·빌드 인자에 넣지 않는다 → Kubernetes Secret 으로 주입.
FROM tomcat:10.1-jre17-temurin

ARG GIT_COMMIT=unknown
ENV GIT_COMMIT=${GIT_COMMIT} \
    APP_STORAGE_DIR=/data/attachments \
    SPRING_PROFILES_ACTIVE=prod \
    JAVA_OPTS="-XX:MaxRAMPercentage=75 -Djava.security.egd=file:/dev/./urandom"

# 기본 예제 앱 제거 후 루트 경로(/)에 배치 → ALB·Probe 경로가 /health 로 고정된다
RUN rm -rf /usr/local/tomcat/webapps/* \
 && groupadd -r app && useradd -r -g app -d /usr/local/tomcat app \
 && mkdir -p /data/attachments \
 && chown -R app:app /usr/local/tomcat /data
COPY --chown=app:app app/target/notice.war /usr/local/tomcat/webapps/ROOT.war

USER app
EXPOSE 8080
# /data/attachments 는 온프레미스 NFS 또는 EKS EFS PVC 를 마운트한다
VOLUME ["/data/attachments"]
