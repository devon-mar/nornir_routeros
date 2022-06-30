#!/bin/bash

SSH_USER="admin"
SSH_HOST="localhost"
SSH_PORT="2222"
SSH_PASS=""

set -x

for i in {1..20}
do
    ssh-keyscan -p 2222 localhost
    if [ $? -eq 0 ]; then
        break
    fi
    echo -e "\033[0;33mNot started yet ($i)\033[0m"
    sleep 10
done

set -e

sshpass -p "$SSH_PASS" sftp -b - -oPort="$SSH_PORT" -oStrictHostKeyChecking=no "$SSH_USER@$SSH_HOST" <<EOF
    put tests/router.crt
    put tests/router.key
    exit
EOF

sshpass -p "$SSH_PASS" ssh -p "$SSH_PORT" -o StrictHostKeyChecking=no -T "$SSH_USER@$SSH_HOST" <<EOF
    /certificate import file-name=router.crt passphrase="" name=router
    /certificate import file-name=router.key passphrase=""
    /ip service set api disabled=no
    /ip service set api-ssl disabled=no certificate=router
EOF
