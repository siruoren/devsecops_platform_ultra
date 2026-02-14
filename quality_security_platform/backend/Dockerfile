FROM python:3.11-alpine
LABEL maintainer="Quality Security Platform"
LABEL version="1.0"

# 环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai \
    DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app

# 安装依赖
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libpq-dev \
    netcat-openbsd \
    openldap-dev \
    openssl-dev \
    tzdata \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 设置文件权限
RUN chmod +x /app/scripts/entrypoint.sh \
    && chmod +x /app/scripts/entrypoint-celery.sh \
    && chmod +x /app/scripts/init_db.py

# 创建必要的目录
RUN mkdir -p /app/static \
    && mkdir -p /app/media \
    && chmod 755 /app/static \
    && chmod 755 /app/media

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/admin/ || exit 1

# 入口点
ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "60"]
