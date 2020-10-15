# bin/bash
# 外部ライブラリを取り込んだデプロイ用パケージを作成するバッチ

export PKG_DIR="python"

sudo rm -rf ${PKG_DIR} && mkdir -p ${PKG_DIR}

docker run --rm -v $(pwd):/foo -w /foo lambci/lambda:build-python3.8 \
    pip3 install -r requirements.txt -t ${PKG_DIR}

cd ${PKG_DIR}

zip -r9 ../handler.zip ./ ../handler.py 
cd ..

sudo rm -rf ${PKG_DIR}