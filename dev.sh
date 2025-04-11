#!/bin/bash
# dev.sh - Helper script for Buridan UI development
# Usage:
#   ./dev.sh components sidebars cards
#   ./dev.sh charts line bar
#   ./dev.sh both sidebars line

MODE=$1
shift

case $MODE in
  components)
    export BURIDAN_DEV_MODE=true
    export BURIDAN_COMPONENTS=$(echo $@ | tr ' ' ',')
    unset BURIDAN_CHARTS
    echo "Development mode: Components only - ${BURIDAN_COMPONENTS}"
    ;;
  charts)
    export BURIDAN_DEV_MODE=true
    export BURIDAN_CHARTS=$(echo $@ | tr ' ' ',')
    unset BURIDAN_COMPONENTS
    echo "Development mode: Charts only - ${BURIDAN_CHARTS}"
    ;;
  both)
    # First argument is component, second is chart
    export BURIDAN_DEV_MODE=true
    export BURIDAN_COMPONENTS=$1
    export BURIDAN_CHARTS=$2
    echo "Development mode: Components - ${BURIDAN_COMPONENTS}, Charts - ${BURIDAN_CHARTS}"
    ;;
  off)
    unset BURIDAN_DEV_MODE
    unset BURIDAN_COMPONENTS
    unset BURIDAN_CHARTS
    echo "Development mode: Disabled (loading all components)"
    ;;
  *)
    echo "Invalid mode. Use: components, charts, both, or off"
    exit 1
    ;;
esac

# Run Reflex
reflex run