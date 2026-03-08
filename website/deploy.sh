#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

S3_BUCKET="minimax-villamarket-website"
CF_DISTRIBUTION="E2AFMAXJ9YXUTH"

echo "=== Building MiniMax Website ==="
npm run build

echo ""
echo "=== Deploying to S3 ==="
aws s3 sync dist/ "s3://$S3_BUCKET/" --delete --region us-east-1

echo ""
echo "=== Invalidating CloudFront ==="
aws cloudfront create-invalidation \
    --distribution-id "$CF_DISTRIBUTION" \
    --paths "/*" \
    --region us-east-1

echo ""
echo "=== Done ==="
echo "Site: https://minimax.villamarket.ai/"
