[Unit]
Description=posio
After=network.target

[Service]
User={{ ansible_ssh_user }}
WorkingDirectory=/home/{{ ansible_ssh_user }}/posio
ExecStart=/home/{{ ansible_ssh_user }}/virtualenvs/posio/bin/python3 -m gunicorn -b 0.0.0.0 --worker-class eventlet -w 1 posio:app
Restart=always

[Install]
WantedBy=multi-user.target