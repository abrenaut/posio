Tested with Ubuntu 18.04

Create a `inventory.ini` file with the following content

```ini
server_address ansible_user=ubuntu server_name=your.server.com
```

and run

```bash        
ansible-playbook -i inventory.ini deploy.yml
```
