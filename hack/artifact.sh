#!/usr/bin/env bash

source ../.env

# Default values
DOCKER_USER="${DOCKER_USER:-}"
DOCKER_PASSWORD="${DOCKER_PASSWORD:-}"
SRC_DIR="../src"
MAX_VERSIONS=3 # Maximum number of versions to keep
DOCKER_BUILD=true

# RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

# Function for colorized loguru_logging
log() {
  local color=$1
  shift
  # shellcheck disable=SC2145
  echo -e "${color}$@${NC}"
}

# Function to display usage instructions
show_help() {
  echo "Usage: ./start.sh [OPTIONS]"
  echo "Docker builds and pushes Docker images to Docker Hub for each folder in the source directory that contains a Dockerfile."
  echo
  echo "Options:"
  echo "  -u, --username   Docker Hub or PyPI username (required)"
  echo "  -p, --password   Docker Hub or PyPI password (required)"
  echo "  -d, --directory  Source directory path (default: ../src)"
  echo "  -h, --help       Show help information"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
  -u | --username)
    DOCKER_USER="$2"
    shift # past argument
    shift # past value
    ;;
  -p | --password)
    DOCKER_PASSWORD="$2"
    shift # past argument
    shift # past value
    ;;
  -d | --directory)
    SRC_DIR="$2"
    shift # past argument
    shift # past value
    ;;
  -h | --help)
    show_help
    exit 0
    ;;
  *) # unknown option
    echo "ERROR: Unknown option: $key"
    show_help
    exit 1
    ;;
  esac
done

create_docker_images() {
  # Iterate through each folder in the source directory
  for folder in "$SRC_DIR"/*/; do
    # Check if the folder contains a Dockerfile
    if [[ -f "$folder/Dockerfile" && "$DOCKER_BUILD" == true ]]; then
      # Extract the folder name
      folder_name=$(basename "$folder")

      # Login to Docker Hub
      log "${GREEN}" "Logging in to Docker Hub...${NC}"
      echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USER" --password-stdin

      # Docker build the Docker image
      log "${GREEN}" "Docker building Docker image for $folder_name...${NC}"
      docker build -t "$folder_name" "$folder"

      # Increment the Docker tag version
      next_version=latest
      log "${YELLOW}next_version=$next_version${NC}"

      # Tag the Docker image with the Docker Hub repository and version
      tag="${DOCKER_USER}/${folder_name}:${next_version}"
      docker tag "$folder_name" "$tag"

      # Push the Docker image to Docker Hub
      log "${GREEN}" "Pushing Docker image to Docker Hub...${NC}"
      docker push "$tag"

      # Delete old versions of the Docker image
      log "${GREEN}" "Deleting old versions of the Docker image...${NC}"
      docker images "${DOCKER_USER}/${folder_name}" --format '{{.ID}} {{.Tag}}' |
        sort -rn | awk -v max_versions="$MAX_VERSIONS" 'NR > max_versions {print $1}' |
        xargs -r docker rmi -f

      # Logout from Docker Hub
      log "${GREEN}" "Logging out from Docker Hub...${NC}"
      docker logout
    fi
  done
}

# Check if required flags are provided
if [[ -z "$DOCKER_PASSWORD" ]]; then
  echo "ERROR: username and password are required."
  exit 1
fi

create_docker_images
