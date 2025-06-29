FROM python:3.13-slim

WORKDIR /app

# システムパッケージの更新とcurlのインストール（ヘルスチェック用）
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# 依存関係のコピーとインストール
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

# ソースコードのコピー
COPY src/ ./src/
COPY langgraph.json ./

# 出力ディレクトリの作成
RUN mkdir -p outputs logs

# ヘルスチェック用のスクリプト
COPY deployment/healthcheck.py ./

EXPOSE 8000

# ヘルスチェックの設定
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python healthcheck.py

CMD ["uv", "run", "langgraph", "up", "--port", "8000", "--host", "0.0.0.0"]
