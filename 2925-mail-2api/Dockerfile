ARG BASE_IMAGE=m.daocloud.io/docker.io/library/python:3.11-slim
FROM ${BASE_IMAGE}

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY server.py .

# 暴露端口
EXPOSE 8003

# 启动应用
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8003"]
