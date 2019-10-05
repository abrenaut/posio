server {
    listen 80;
    server_name {{ server_name }};

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:5000;
    }

    location /static {
        alias /home/{{ ansible_ssh_user }}/posio/app/static;
        expires 30d;
    }

    location /socket.io {
        include proxy_params;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_pass http://127.0.0.1:5000/socket.io;
    }
}
