#!/bin/bash
set -Eeuo pipefail
source ./venv/bin/activate
git pull

pip install -r requirements.txt
npm ci --dev
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
python manage.py collectstatic --noinput
python manage.py migrate --noinput
systemctl daemon-reload
systemctl reload starburger.service
systemctl reload nginx.service

if [ -f .env ]; then
  export $(echo $(cat .env | sed 's/#.*//g'| xargs -0) | envsubst)
fi

LOCAL_USERNAME=$(whoami)
REVISION=$(git rev-parse --short HEAD)

echo "Code version is:" "$REVISION"
echo "Environment:" "$ROLLBAR_ENVIRONMENT"

curl https://api.rollbar.com/api/1/deploy/ \
  -F access_token="$ROLLBAR_ACCESS_TOKEN" \
  -F environment="$ROLLBAR_ENVIRONMENT" \
  -F revision="$REVISION" \
  -F local_username="$LOCAL_USERNAME"

printf "\nDeploy completed!\n"
