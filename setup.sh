sudo apt update
sudo apt install -y python3 python3-pip python3-dev
sudo pip3 install -r requirements.txt
sudo mv /cuba/cuba-cameras-monitoring/cuba-cameras-monitoring.service /lib/systemd/system/cuba-cameras-monitoring.service
sudo systemctl daemon-reload
sudo systemctl enable cuba-cameras-monitoring.service
sudo systemctl start cuba-cameras-monitoring.service
sudo systemctl status cuba-cameras-monitoring.service
