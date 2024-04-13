# Python 3.10.4-slimベースイメージを使用
FROM python:3.10.4-slim

# ポート8501を公開（Streamlit用）
EXPOSE 8501

# 作業ディレクトリを設定
WORKDIR /usr/src/app

# システム依存関係のインストール
# apt-get updateとapt-get installを一つのRUN命令で実行して不要なレイヤを削減
RUN apt-get update && apt-get install -y \
    # pyaudioの依存関係
    portaudio19-dev \
    # 一部の音声処理ライブラリ用
    libflac-dev \
    # Tesseract-OCR用
    tesseract-ocr \
    # Tesseract-OCR開発用ライブラリ
    libtesseract-dev \
    # zshのインストール
    zsh \
    && rm -rf /var/lib/apt/lists/*


# Pythonの依存関係ファイルをコピーしてインストール
COPY requirements.txt ./

# Add these lines before the `RUN pip install` command to install build essentials
RUN apt-get update && apt-get install -y \
    gcc \
    libasound2-dev \
    portaudio19-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのファイルをコピー
COPY . .

# 環境変数の設定
ENV PYTHONUNBUFFERED=1

# アプリケーションの実行コマンド（Streamlit）
ENTRYPOINT ["streamlit", "run"]
CMD ["streamlit_app.py"]

# ユーザーのデフォルトシェルをzshに変更（必要に応じてコメントを外す）
# RUN chsh -s /usr/bin/zsh

