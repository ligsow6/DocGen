#!/usr/bin/env bash
# Automatic Doxygen + DocGen update script
# Usage: ./update_docs.sh --repo /path/to/repo [--open]

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

REPO_DIR=""
OPEN_FLAG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO_DIR="$2"
      shift 2
      ;;
    --open)
      OPEN_FLAG="--open"
      shift
      ;;
    *)
      echo -e "${RED}Unknown argument: $1${NC}"
      exit 1
      ;;
  esac
 done

if [[ -z "$REPO_DIR" ]]; then
  REPO_DIR="$(pwd)"
fi

if [[ ! -d "$REPO_DIR" ]]; then
  echo -e "${RED}Error: repo not found: $REPO_DIR${NC}"
  exit 1
fi

DOXYFILE_PATH=""
if [[ -f "$REPO_DIR/Doxyfile" ]]; then
  DOXYFILE_PATH="$REPO_DIR/Doxyfile"
elif [[ -f "$REPO_DIR/docs/Doxyfile" ]]; then
  DOXYFILE_PATH="$REPO_DIR/docs/Doxyfile"
fi

OUTPUT_DIR="$REPO_DIR/DocGen/api"
BACKUP_DIR="$REPO_DIR/DocGen/api_backup_$(date +%Y%m%d_%H%M%S)"

echo -e "${BLUE}=== DocGen + Doxygen Update ===${NC}"
echo -e "${BLUE}Repo: $REPO_DIR${NC}"

if command -v docgen &> /dev/null; then
  echo -e "${YELLOW}Running DocGen build...${NC}"
  docgen build --repo "$REPO_DIR" --doxygen || {
    echo -e "${RED}DocGen build failed${NC}"
    exit 1
  }
  echo -e "${GREEN}✓ DocGen build completed${NC}"
  if [[ "$OPEN_FLAG" == "--open" ]] && [[ -f "$OUTPUT_DIR/html/index.html" ]] && command -v xdg-open &> /dev/null; then
    echo -e "${BLUE}Opening documentation in browser...${NC}"
    xdg-open "$OUTPUT_DIR/html/index.html" &
  fi
  exit 0
else
  echo -e "${YELLOW}DocGen CLI not found in PATH, skipping build${NC}"
fi

if [[ -z "$DOXYFILE_PATH" ]]; then
  echo -e "${YELLOW}No Doxyfile found. Skipping Doxygen.${NC}"
  exit 0
fi

if ! command -v doxygen &> /dev/null; then
  echo -e "${RED}Error: Doxygen is not installed or not found in PATH${NC}"
  echo -e "${YELLOW}To install on Ubuntu/Debian: sudo apt-get install doxygen${NC}"
  echo -e "${YELLOW}To install on Fedora/CentOS: sudo yum install doxygen${NC}"
  echo -e "${YELLOW}To install on Arch: sudo pacman -S doxygen${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Doxygen found: $(doxygen --version)${NC}"
echo -e "${GREEN}✓ Doxyfile found: $DOXYFILE_PATH${NC}"

if [[ -d "$OUTPUT_DIR" ]]; then
  echo -e "${YELLOW}Backing up old documentation...${NC}"
  cp -r "$OUTPUT_DIR" "$BACKUP_DIR"
  echo -e "${GREEN}✓ Backup created: $BACKUP_DIR${NC}"
fi

if [[ -d "$OUTPUT_DIR" ]]; then
  echo -e "${YELLOW}Cleaning old documentation...${NC}"
  rm -rf "$OUTPUT_DIR"/*
fi

echo -e "${YELLOW}Generating Doxygen documentation...${NC}"
cd "$REPO_DIR"

if doxygen "$DOXYFILE_PATH"; then
  echo -e "${GREEN}✓ Documentation generated successfully!${NC}"

  if [[ -d "$OUTPUT_DIR/html" ]]; then
    HTML_FILES=$(find "$OUTPUT_DIR/html" -name "*.html" | wc -l)
    echo -e "${GREEN}✓ $HTML_FILES HTML files generated${NC}"
    echo -e "${GREEN}✓ Documentation available at: $OUTPUT_DIR/html/index.html${NC}"

    if [[ "$OPEN_FLAG" == "--open" ]] && command -v xdg-open &> /dev/null; then
      echo -e "${BLUE}Opening documentation in browser...${NC}"
      xdg-open "$OUTPUT_DIR/html/index.html" &
    fi
  fi

  if [[ -d "$BACKUP_DIR" ]]; then
    echo -e "${YELLOW}Removing backup (generation successful)...${NC}"
    rm -rf "$BACKUP_DIR"
  fi

  echo -e "${GREEN}=== Update completed successfully! ===${NC}"
else
  echo -e "${RED}Error during documentation generation${NC}"

  if [[ -d "$BACKUP_DIR" ]]; then
    echo -e "${YELLOW}Restoring backup...${NC}"
    rm -rf "$OUTPUT_DIR"
    mv "$BACKUP_DIR" "$OUTPUT_DIR"
    echo -e "${GREEN}✓ Old documentation restored${NC}"
  fi

  exit 1
fi
