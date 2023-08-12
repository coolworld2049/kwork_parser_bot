#!/usr/bin/env bash

source .env

startup() {
  docker-compose  up -d ngrok
  echo "Please enter ngrok https endpoint url ( https://dashboard.ngrok.com/cloud-edge/endpoints ):"
  read webhook_endpoint
  WEBHOOK_URL=${webhook_endpoint} docker-compose  up -d telegram-bot

}

shutdown() {
  docker-compose down --rmi local --remove-orphans
}

print_usage() {
  echo "Usage: $0 [OPTION]"
  echo "Options:"
  echo "  startup           Bring up containers using Docker Compose"
  echo "  shutdown          Remove containers, images"
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
--help)
  print_usage
  ;;
*)
  echo "Invalid option: $1"
  print_usage
  exit 1
  ;;
esac
