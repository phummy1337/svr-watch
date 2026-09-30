#!/bin/sh
# Wrap the artifact page source (svr-watch.html) into a standalone index.html for GitHub Pages.
cd "$(dirname "$0")"
{ printf '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<meta name="robots" content="noindex">\n'
  cat svr-watch.html
  printf '\n</html>\n'; } > index.html
