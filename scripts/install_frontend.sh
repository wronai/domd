#!/bin/bash
# Script to install frontend dependencies

echo "Installing frontend dependencies..."
cd frontend && npm install --legacy-peer-deps
