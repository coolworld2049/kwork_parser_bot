#!/bin/bash

source env

GREEN='\033[0;32m'
NC='\033[0m'
LOG_FILE=bench_results.log

# Set the default PostgresSQL connection parameters
DEFAULT_PGHOST=${DEFAULT_PGHOST:-"localhost"}
DEFAULT_PGPORT=${DEFAULT_PGPORT:-"5432"}
PGUSER=${PGUSER:-"postgres"}
PGDATABASE=${PGDATABASE:-"app"}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-"postgres"}
export PGPASSWORD="$POSTGRES_PASSWORD"

# Set the number of threads and duration for the tests
THREADS="$(grep ^cpu\\scores /proc/cpuinfo | uniq | awk '{print $4}')"
SCALE=${SCALE:-50}
CLIENTS=${CLIENTS:-300}
TX_MUL=${TX_MUL:-5}
START="${START:-50}"
STEP="${STEP:-50}"
REVERT=false
FIXED_TRANSACTION_SIZE=""

# Function to display usage instructions
show_help() {
  echo "Usage: ./pgbench.sh [OPTIONS]"
  echo "Run pgbench test with configurable PostgresSQL connection parameters."
  echo
  echo "Options:"
  echo "  --tpcb              Run TPC_B test"
  echo "  --select            Run select_only test"
  echo "  -h,--host            PostgresSQL server hostname (default: $DEFAULT_PGHOST)"
  echo "  -p,--port            PostgresSQL server port (default: $DEFAULT_PGPORT)"
  echo "  -r,--revert          Swap clients(default: ${CLIENTS}) and transactions(default: clients * <TX_MUL>${TX_MUL}) size"
  echo "  -ft,--fixed-transaction-size  <number>"
  echo "  -u,--username        PostgresSQL username (default: $PGUSER)"
  echo "  -P,--password        PostgresSQL password (default: $POSTGRES_PASSWORD)"
  echo "  --help              Show help information"
  echo "Examples:"
  echo "  bash pgbench.sh --host auth-postgresql-slave --port 5433 --select -u myuser -P mypassword"
  echo "  bash pgbench.sh --host auth-postgresql-primary --port 5432 --tpcb -u myuser -P mypassword"
}

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then
  echo "Please run this script with sudo."
  exit 1
fi

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
  -h | --host)
    PGHOST="$2"
    shift # past argument
    shift # past value
    ;;
  -p | --port)
    PGPORT="$2"
    shift # past argument
    shift # past value
    ;;
  -u | --username)
    PGUSER="$2"
    shift # past argument
    shift # past value
    ;;
  -P | --password)
    POSTGRES_PASSWORD="$2"
    export PGPASSWORD="$POSTGRES_PASSWORD"
    shift # past argument
    shift # past value
    ;;
  --tpcb)
    TEST="TPC_B"
    shift # past argument
    ;;
  --select)
    TEST="select_only"
    shift # past argument
    ;;
  -r | --revert)
    REVERT=true
    shift # past argument
    ;;
  -ft | --fixed-transaction-size)
    FIXED_TRANSACTION_SIZE="$2"
    shift
    shift # past argument
    ;;
  --help)
    show_help
    exit 0
    ;;
  *) # unknown option
    echo "ERROR: Unknown option: $key"
    exit 1
    ;;
  esac
done

# Set the PostgresSQL connection parameters
PGHOST="${PGHOST:-$DEFAULT_PGHOST}"
PGPORT="${PGPORT:-$DEFAULT_PGPORT}"

function init() {
  pgbench -i -s "$SCALE" -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" "$PGDATABASE" | tee $LOG_FILE
}

function result_msg() {
  echo -e "${GREEN}test_type=$TEST, clients=$1, transactions=$2${NC}"
}

function TPC_B() {
  result_msg "$1" "$2"
  pgbench -j "$THREADS" -c "$1" -t "$2" -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" "$PGDATABASE" | tee $LOG_FILE
}

function select_only() {
  result_msg "$1" "$2"
  pgbench -b select-only -j "$THREADS" -c "$1" -t "$2" -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" "$PGDATABASE" | tee $LOG_FILE
}

init
for i in $(seq "$START" "$STEP" "$CLIENTS"); do
  sleep 1
  if [[ "$FIXED_TRANSACTION_SIZE" ]]; then
    j="$FIXED_TRANSACTION_SIZE"
  else
    j="$(("$i" * "$TX_MUL"))"
  fi
  # Run the selected tests
  if [ "$REVERT" = true ]; then
    _tmp="$i"
    i="$j"
    j="$_tmp"
  fi
  if [ "$TEST" == "TPC_B" ]; then
    TPC_B "$i" "$j"
  elif [ "$TEST" == "select_only" ]; then
    select_only "$(("$i" * 2))" "$(("$j" * 10))"
  else
    break
    show_help
  fi
  printf "\n"
done
