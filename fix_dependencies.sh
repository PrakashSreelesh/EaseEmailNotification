#!/bin/bash

# Quick Fix Script for Terminal Errors
# Resolves: ModuleNotFoundError: No module named 'prometheus_client'

echo "=========================================="
echo "  Installing Missing Dependencies"
echo "=========================================="

# Install prometheus_client
pip install prometheus_client

echo ""
echo "✅ Dependencies installed!"
echo ""
echo "=========================================="
echo "  Now restart your Celery workers:"
echo "=========================================="
echo ""
echo "Terminal 1 (Email Worker):"
echo "  celery -A app.worker.celery_config worker -Q email_delivery -c 4"
echo ""
echo "Terminal 2 (Webhook Worker):"
echo "  celery -A app.worker.celery_config worker -Q webhook_delivery -c 2"
echo ""
echo "=========================================="
