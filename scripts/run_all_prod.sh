#!/bin/bash
# Run all services in production mode (using systemd)

echo "Starting services via systemd..."

sudo systemctl start intrusion-detection
sudo systemctl start intrusion-backend
sudo systemctl start intrusion-frontend

echo "Services started. Check status with:"
echo "  sudo systemctl status intrusion-detection"
echo "  sudo systemctl status intrusion-backend"
echo "  sudo systemctl status intrusion-frontend"

