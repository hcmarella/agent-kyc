#!/bin/bash
set -e

FROM_ENV=$1
TO_ENV=$2

if [ -z "$FROM_ENV" ] || [ -z "$TO_ENV" ]; then
  echo "Usage: ./scripts/promote.sh dev sit"
  echo "Usage: ./scripts/promote.sh sit sat"
  echo "Usage: ./scripts/promote.sh sat prod"
  exit 1
fi

FROM_FILE="environments/$FROM_ENV/values.yaml"
TO_FILE="environments/$TO_ENV/values.yaml"

TAG=$(grep "tag:" "$FROM_FILE" | awk '{print $2}')
REPO=$(grep "repository:" "$FROM_FILE" | awk '{print $2}')

echo "Promoting image:"
echo "Repository: $REPO"
echo "Tag: $TAG"
echo "From: $FROM_ENV"
echo "To: $TO_ENV"

sed -i "" "s|repository:.*|repository: $REPO|g" "$TO_FILE"
sed -i "" "s|tag:.*|tag: $TAG|g" "$TO_FILE"
sed -i "" "s|pullPolicy:.*|pullPolicy: Always|g" "$TO_FILE"

git add "$TO_FILE"
git commit -m "Promote $TAG from $FROM_ENV to $TO_ENV"
git push
