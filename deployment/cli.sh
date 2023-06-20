#!/usr/bin/env bash

source ../src/${PROJECT_NAME?env PROJECT_NAME required}/.env

project_name=${PROJECT_NAME?env PROJECT_NAME required}
compose_file=docker-compose.yml

install() {
  docker pull coolworldocker/"$project_name"
  docker-compose -p "$project_name" -f "$compose_file" up -d bot
}

delete() {
  docker-compose -p "$project_name" -f "$compose_file" down --rmi local --remove-orphans
}

print_usage() {
  echo "Usage: $0 [OPTION]"
  echo "Options:"
  echo "  install           Bring up containers using Docker Compose"
  echo "  delete            Remove containers, images"
  echo "  --help            Display this help message"
}

# Parse command-line options
if [[ $# -eq 0 ]]; then
  print_usage
  exit 1
fi

case $1 in
install)
  install
  ;;
delete)
  delete
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
