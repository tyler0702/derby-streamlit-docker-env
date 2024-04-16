# docker とは？

Docker は、特別な箱のようなものだと考えることができます。この箱の中には、アプリケーションを動かすのに必要なすべてのもの（プログラム、ライブラリ、ツールなど）が入っていて、どんなコンピューター上でも同じように動くようになっています。

例えば、あなたがレゴブロックで作った作品を持って友達の家に遊びに行くとき、その作品をそのまま持って行くと途中で壊れたり、部品がなくなったりするかもしれませんね。でも、それを透明な箱にきちんと入れて持っていけば、壊れる心配もなく、友達の家でもきちんと展示できます。

Docker はその透明な箱のようなもので、アプリケーションが「どこでもきちんと動く」ように保護してくれます。だから、開発者は自分のコンピューターで作ったアプリケーションを、他の人のコンピューターやインターネット上のサーバーでも、全く同じように簡単に動かすことができるのです。

# ここでの Docker の使い方ステップ

1. Docker Desktop をインストール して立ち上げる
   https://www.docker.com/ja-jp/products/docker-desktop

2. Docker Hub にてアカウントを作成する  
   https://hub.docker.com/

3. このリポジトリを好きなディレクトリにクローンする

4. クローンが完了したら、terminal で docker-compose.yml が置いてあるディレクトリに移動

```
cd 「docker-compose.ymlが置いてあるディレクトリ」
```

5. 下記のコマンドを実行

```
docker-compose build --no-cache
```

6. ビルドが終わったら下記のコマンドを実行

```
docker-compose up -d
```

7. streamlit がちゃんと立ち上がっているか確認する。下記の URL にアクセスして streamlit が立ち上がっていたら成功！  
   URL: http://localhost:8501

8. 補足: /src 配下にある streamlit_app.py を編集する  
   このファイルを修正すれば反映されます〜

## docker を落とす時

```
docker-compose down
```

これで streamlit も落ちてます〜

## docker をまた立ち上げたい時

```
docker-compose up -d
```

## docker の再起動（落として立ち上げる）

上記の docker-compose down と docker-compose up -d を同時にしてくれるコマンド

```
docker-compose restart
```

## requirements.txt を変更した時

再ビルドが必要です。

```
docker-compose build --no-cache

ビルド終わったら
docker-compose up -d
```

## .env 環境変数ファイルに関して

環境変数ファイルは Git には共有してはいけません。  
なので、Slack でお送りまします！
保管場所は /src/streamlit_app.py と同じディレクトリに保存してください。
