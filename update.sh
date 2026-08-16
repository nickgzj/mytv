#!/bin/sh
set -eu
curl -L --fail --retry 3 -o /tmp/index.m3u https://iptv-org.github.io/iptv/index.m3u
python3 build.py
