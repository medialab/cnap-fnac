#!/bin/bash

source config.sh 2> /dev/null
if [ ! -s config.sh ] || [ -z "$SERVERROOT" ]; then
  echo "First create and fill config.sh with SERVERROOT and VAULT from config.sh.example" 1>&2
  exit 1
fi

mkdir -p cache data db
function escapeit { perl -e 'use URI::Escape; print uri_escape shift();print"\n"' "$1" | sed 's/\s/_/g'; }
function cachedcurl {
  url="$SERVERROOT/$VAULT/$1"
  cache="cache/"$(escapeit "$url")
  retries=$2
  if [ -z "$retries" ]; then retries=3; fi
  if test -s "$cache" && grep '^{"' "$cache" > /dev/null; then
    cat "$cache"
  elif [ "$retries" -eq 0 ]; then
    echo "ERROR downloading $url in $cache.tmp after 3 retries" 1>&2
  else
    curl -sL "$url" > "$cache.tmp"
    if ! grep '^{"' "$cache.tmp" > /dev/null; then
      echo "INFO $retries retries for $url" 1>&2
      cachedcurl "$1" $(($retries - 1))
    else
      mv "$cache.tmp" "$cache"
      cat "$cache"
    fi
  fi
}

total=$(cachedcurl "artworks?size=0" | python -m json.tool | grep '"totalCount"' | sed 's/[^0-9]//g')
echo "RESULTS to collect: $total" 1>&2

resperpage=1000
for i in `seq 0 $(($total / $resperpage))`; do
  firstres=$(($i * $resperpage))
  lastres=$(($firstres + $resperpage -1))
  if [ $lastres -gt $total ]; then lastres=$total; fi
  cachedcurl "artworks?size=$resperpage&from=$firstres&sort=source.artwork._id:asc" > "data/artworks-$firstres-$lastres.json"
done

./assemble_results.py data/artworks-*0*.json > data/artworks-all.json

