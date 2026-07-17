#!/bin/sh
set -eu

ENV_FILE=${1:-.env}
PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$PROJECT_DIR"

if [ ! -f "$ENV_FILE" ]; then
    echo "Environment file not found: $ENV_FILE" >&2
    exit 1
fi

read_env_value() {
    sed -n "s/^$1=//p" "$ENV_FILE" | tail -n 1 | tr -d '\r'
}

DOMAIN=${DOMAIN:-$(read_env_value DOMAIN)}
LETSENCRYPT_EMAIL=${LETSENCRYPT_EMAIL:-$(read_env_value LETSENCRYPT_EMAIL)}
DOMAIN=$(printf '%s' "$DOMAIN" | sed 's/^"//;s/"$//')
LETSENCRYPT_EMAIL=$(printf '%s' "$LETSENCRYPT_EMAIL" | sed 's/^"//;s/"$//')

: "${DOMAIN:?Set DOMAIN in $ENV_FILE}"
: "${LETSENCRYPT_EMAIL:?Set LETSENCRYPT_EMAIL in $ENV_FILE}"

case "$DOMAIN" in
    *[!A-Za-z0-9.-]*|'')
        echo "DOMAIN contains unsupported characters: $DOMAIN" >&2
        exit 1
        ;;
esac

command -v docker >/dev/null 2>&1 || {
    echo "Docker is required." >&2
    exit 1
}
command -v openssl >/dev/null 2>&1 || {
    echo "OpenSSL is required for the temporary certificate." >&2
    exit 1
}

compose() {
    docker compose --env-file "$ENV_FILE" -f compose.yaml "$@"
}

CERT_ROOT=deploy/certbot/conf
LIVE_DIR="$CERT_ROOT/live/$DOMAIN"
ARCHIVE_DIR="$CERT_ROOT/archive/$DOMAIN"
RENEWAL_FILE="$CERT_ROOT/renewal/$DOMAIN.conf"

mkdir -p deploy/certbot/www "$LIVE_DIR"

if [ -f "$LIVE_DIR/fullchain.pem" ] && [ -f "$RENEWAL_FILE" ]; then
    echo "A managed certificate already exists for $DOMAIN."
    compose up -d
    exit 0
fi

echo "Creating a temporary certificate for $DOMAIN..."
openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
    -keyout "$LIVE_DIR/privkey.pem" \
    -out "$LIVE_DIR/fullchain.pem" \
    -subj "/CN=$DOMAIN" >/dev/null 2>&1

echo "Starting Nginx and its dependencies..."
compose up -d nginx

attempt=0
until compose exec -T nginx nginx -t >/dev/null 2>&1; do
    attempt=$((attempt + 1))
    if [ "$attempt" -ge 30 ]; then
        echo "Nginx did not become ready. Check: docker compose logs nginx" >&2
        exit 1
    fi
    sleep 2
done

echo "Requesting a Let's Encrypt certificate..."
rm -rf "$LIVE_DIR" "$ARCHIVE_DIR"
rm -f "$RENEWAL_FILE"

compose run --rm --entrypoint certbot certbot certonly \
    --webroot \
    --webroot-path /var/www/certbot \
    --domain "$DOMAIN" \
    --email "$LETSENCRYPT_EMAIL" \
    --rsa-key-size 4096 \
    --agree-tos \
    --no-eff-email \
    --non-interactive

echo "Reloading Nginx with the issued certificate..."
compose exec -T nginx nginx -s reload
compose up -d

echo "HTTPS is ready at https://$DOMAIN"