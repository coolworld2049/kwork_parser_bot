#!/usr/bin/env bash

cd kwork_parser_bot

source ./.env

startup() {
  AUTH_TOKEN=${NGROK_AUTH_TOKEN} docker-compose  up -d ngrok
  echo "Please enter ngrok https endpoint url ( https://dashboard.ngrok.com/cloud-edge/endpoints ):"
  read webhook_endpoint
  WEBHOOK_URL=${webhook_endpoint} docker-compose  up -d telegram-bot

}

dev() {
  docker-compose -f docker-compose.dev.yml up -d
}
shutdown() {
  docker-compose down --rmi local --remove-orphans
}

print_usage() {
  echo "Usage: $0 [OPTION]"
  echo "Options:"
  echo "  startup           Bring up containers using Docker Compose"
  echo "  shutdown          Remove containers, images"
  echo "  dev               development mode"
  echo "  --help            Display this help message"
}

# Parse command-line options
if [[ $# -eq 0 ]]; then
  print_usage
  exit 1
fi

case $1 in
startup)
  startup
  ;;
shutdown)
  shutdown
  ;;
dev)
  dev
  ;;
--help)
  print_usage
  ;;
*)
  echo "Invalid option: $1"
  print_usage
  exit 1
  ;;
esac

cd ..