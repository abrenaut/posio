[Unit]
Description=posio
After=network.target

[Service]
User={{ ansible_ssh_user }}
WorkingDirectory=/home/{{ ansible_ssh_user }}/posio
ExecStart=/home/{{ ansible_ssh_user }}/virtualenvs/posio/bin/python3 /home/{{ ansible_ssh_user }}/posio/run.py
Restart=always

[Install]
WantedBy=multi-user.target