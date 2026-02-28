#!/bin/bash
# Fix firewall to allow Docker containers to access Ollama

set -e

echo "🔥 Fixing Firewall for Ollama Access"
echo "====================================="
echo ""

HOST_IP=$(hostname -I | awk '{print $1}')
echo "📍 Host IP: $HOST_IP"
echo ""

# Check current firewall status
echo "🔍 Checking current firewall rules..."
if sudo iptables -L -n | grep -q "11434"; then
    echo "⚠️  Found existing rules for port 11434"
    sudo iptables -L -n | grep "11434"
else
    echo "ℹ️  No existing rules for port 11434"
fi
echo ""

# Allow connections from Docker network to port 11434
echo "🔧 Adding firewall rule to allow Docker containers..."
echo "   Allowing: 172.16.0.0/12 (Docker networks) -> port 11434"

# Add rule to allow Docker networks (172.16.0.0/12 covers most Docker networks)
sudo iptables -I INPUT -s 172.16.0.0/12 -p tcp --dport 11434 -j ACCEPT

# Also allow from the specific subnet
sudo iptables -I INPUT -s 172.31.0.0/16 -p tcp --dport 11434 -j ACCEPT

# Allow from localhost
sudo iptables -I INPUT -s 127.0.0.1 -p tcp --dport 11434 -j ACCEPT

echo "✅ Firewall rules added"
echo ""

# Show the new rules
echo "📋 Current firewall rules for port 11434:"
sudo iptables -L INPUT -n --line-numbers | grep -E "11434|Chain INPUT"
echo ""

# Test connection
echo "🧪 Testing connection to Ollama..."
if curl -s http://$HOST_IP:11434/api/tags > /dev/null 2>&1; then
    echo "✅ SUCCESS! Ollama is now accessible on $HOST_IP:11434"
else
    echo "❌ Still cannot connect to $HOST_IP:11434"
    echo ""
    echo "Additional troubleshooting:"
    echo "1. Check if Ollama is running: ps aux | grep ollama"
    echo "2. Check what's listening on 11434: sudo netstat -tlnp | grep 11434"
    echo "3. Check Ollama logs: cat /tmp/ollama.log"
    exit 1
fi
echo ""

# Test from Docker container
echo "🐳 Testing from Docker container..."
if docker compose exec backend curl -s http://$HOST_IP:11434/api/tags > /dev/null 2>&1; then
    echo "✅ SUCCESS! Container can reach Ollama!"
else
    echo "⚠️  Container still cannot reach Ollama"
    echo "   Checking Docker network..."
    docker compose exec backend ip route
fi
echo ""

# Make rules persistent (optional)
echo "💾 Making firewall rules persistent..."
if command -v iptables-save > /dev/null 2>&1; then
    sudo iptables-save | sudo tee /etc/iptables/rules.v4 > /dev/null 2>&1 || true
    echo "✅ Rules saved (if iptables-persistent is installed)"
else
    echo "⚠️  iptables-save not found, rules will be lost on reboot"
    echo "   To make permanent, install: sudo apt-get install iptables-persistent"
fi
echo ""

echo "✅ Firewall configuration complete!"
echo ""
echo "Next step: Restart backend and test"
echo "  docker compose restart backend"
echo "  sleep 8"
echo "  curl -X POST http://localhost:8000/analyze -H 'Content-Type: application/json' -d '{\"regulatory_text\":\"Test\",\"repo_path\":\"/app/fake_pix_repo\"}'"
