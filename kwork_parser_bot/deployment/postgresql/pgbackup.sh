#!/bin/bash

SCRIPTDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "$SCRIPTDIR"/../../src/air_delivery_bot/.env

export PGPASSWORD=${POSTGRESQL_PASSWORD:-}

BACKUP_DIR=~/pg_backup
[ -d "$BACKUP_DIR" ] || mkdir -p "$BACKUP_DIR"
DAYS_TO_KEEP=14
FILE_SUFFIX=_"${POSTGRESQL_DATABASE}"_backup.sql
FILE=$(date +"%Y%m%d%H%M")${FILE_SUFFIX}
OUTPUT_FILE=${BACKUP_DIR}/${FILE}

pg_dump -U "$POSTGRESQL_USERNAME" -h 127.0.0.1 -p 5432  -Fp -f "${OUTPUT_FILE}" "${POSTGRESQL_DATABASE}"

gzip "$OUTPUT_FILE"

echo "${OUTPUT_FILE}.gz was created:"
ls -l "${OUTPUT_FILE}".gz

find $BACKUP_DIR -maxdepth 1 -mtime +$DAYS_TO_KEEP -name "*${FILE_SUFFIX}.gz" -exec rm -rf '{}' ';'
