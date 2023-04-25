#!/bin/bash
set -Eeuo pipefail
source ./venv/bin/activate
git pull

#If server is out of memory try this:

#/sbin/swapoff /var/swap.1      # Uncomment for re-use without rebooting server
#/bin/dd if=/dev/zero of=/var/swap.1 bs=1M count=1024
#/sbin/mkswap /var/swap.1
#/sbin/swapon /var/swap.1

pip install -r requirements.txt
npm ci --dev
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
python manage.py collectstatic --noinput
python manage.py migrate --noinput
systemctl daemon-reload
systemctl reload starburger.service
systemctl reload nginx.service

if [ -f .env ]; then
  # shellcheck disable=SC2046
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
