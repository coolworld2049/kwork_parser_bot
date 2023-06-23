#!/usr/bin/env bash
source ../src/kwork_parser_bot/.env

project_name=${PROJECT_NAME?env PROJECT_NAME required}
compose_file=docker-compose.yml

pgbackup() {
  crontab -l >pgcron
  echo "0 */6 * * * ~/$project_name/deployment/postgresql/pgbackup.sh" >>pgcron
  crontab pgcron
  rm pgcron
}

install() {
  docker pull coolworldocker/"$project_name"
  docker-compose -p "$project_name" -f "$compose_file" up -d
  pgbackup
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
