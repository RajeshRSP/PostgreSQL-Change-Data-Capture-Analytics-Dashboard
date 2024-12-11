#!/bin/bash

# Exit on any error
set -e

echo "Step 1: Installing JDK for Kafka..."
sudo apt update
sudo apt install -y openjdk-11-jdk
java -version

echo "Step 2: Creating kafka user and adding to sudo group..."
sudo adduser --gecos "" --disabled-password kafka
echo "Please set a password for kafka user:"
sudo passwd kafka
sudo adduser kafka sudo

echo "Step 3: Downloading and extracting Kafka binaries..."
sudo -u kafka bash << 'EOF'
mkdir -p ~/Downloads
cd ~/Downloads
curl "https://downloads.apache.org/kafka/3.7.0/kafka_2.12-3.7.0.tgz" -o kafka.tgz
mkdir -p ~/kafka
cd ~/kafka
tar -xvzf ~/Downloads/kafka.tgz --strip 1
EOF

echo "Step 4 & 5: Configuring Kafka..."
sudo -u kafka bash << 'EOF'
mkdir -p /home/kafka/logs
sed -i 's|log.dirs=.*|log.dirs=/home/kafka/logs|' ~/kafka/config/server.properties
echo "delete.topic.enable = true" >> ~/kafka/config/server.properties
EOF

echo "Step 6: Creating systemd service files..."
# Create Zookeeper service file
cat << 'EOF' | sudo tee /etc/systemd/system/zookeeper.service
[Unit]
Requires=network.target remote-fs.target
After=network.target remote-fs.target

[Service]
Type=simple
User=kafka
ExecStart=/home/kafka/kafka/bin/zookeeper-server-start.sh /home/kafka/kafka/config/zookeeper.properties
ExecStop=/home/kafka/kafka/bin/zookeeper-server-stop.sh
Restart=on-abnormal

[Install]
WantedBy=multi-user.target
EOF

# Create Kafka service file
cat << 'EOF' | sudo tee /etc/systemd/system/kafka.service
[Unit]
Requires=zookeeper.service
After=zookeeper.service

[Service]
Type=simple
User=kafka
ExecStart=/bin/sh -c '/home/kafka/kafka/bin/kafka-server-start.sh /home/kafka/kafka/config/server.properties > /home/kafka/kafka/kafka.log 2>&1'
ExecStop=/home/kafka/kafka/bin/kafka-server-stop.sh
Restart=on-abnormal

[Install]
WantedBy=multi-user.target
EOF

echo "Step 7: Starting Kafka services..."
sudo systemctl daemon-reload
sudo systemctl start zookeeper
sudo systemctl start kafka
sudo systemctl status kafka

echo "Installation complete! Checking Kafka service status..."
sleep 5
sudo systemctl status kafka

echo "To enable Kafka to start on boot, run:"
echo "sudo systemctl enable zookeeper"
echo "sudo systemctl enable kafka"
