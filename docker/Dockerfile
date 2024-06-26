# Python 3.10.4-slimベースイメージを使用
FROM python:3.10.4-slim

# ポート8501を公開（Streamlit用）
EXPOSE 8501

# 作業ディレクトリを設定
WORKDIR /usr/src/app

# システム依存関係のインストール
# apt-get updateとapt-get installを一つのRUN命令で実行して不要なレイヤを削減
RUN apt-get update && apt-get install -y \
    gcc \
    libasound2-dev \
    portaudio19-dev \
    python3-dev \
    libflac-dev \
    tesseract-ocr \
    libtesseract-dev \
    zsh \
    && rm -rf /var/lib/apt/lists/*


# Pythonの依存関係ファイルをコピーしてインストール
COPY ../requirements.txt .

# # Add these lines before the `RUN pip install` command to install build essentials
# RUN apt-get update && apt-get install -y \
#     gcc \
#     libasound2-dev \
#     portaudio19-dev \
#     python3-dev \
#     && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのファイルをコピー
COPY ../src .

# 環境変数の設定
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_RUN_ON_SAVE=true

# アプリケーションの実行コマンド（Streamlit）
ENTRYPOINT ["streamlit", "run"]
# CMD ["streamlit_app.py","--server.runOnSave=true"]
CMD ["main.py","--server.runOnSave=true"]

# ユーザーのデフォルトシェルをzshに変更（必要に応じてコメントを外す）
# RUN chsh -s /usr/bin/zsh

