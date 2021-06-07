import sys
import openstack
from getpass import getpass

username = input("Enter your username: ")
password = getpass("Enter your password: ")
server_name = input("Enter a name for your server: ")

conn = openstack.connect(cloud='ovh', username=username, password=password)

image = conn.get_image("user-base-0.3.2")
flavor = conn.get_flavor("d2-2")
network = conn.get_network("Ext-Net")

server = conn.get_server(server_name, bare=True)

userdata = """
#cloud-config
disable_root: true
preserve_hostname: false
manage_etc_hosts: true
ssh_pwauth: false
users:
  - name: anadmin
    groups:
      - adm
      - staff
      - sudo
    homedir: /local-home/anadmin
    lock_passwd: false
    hashed_passwd: $6$rounds=4096$Uai52ED7FnpSxVd1$iY6tuSJ2dpm1Owa41NUSvp/H1M39ZnVjiP9OWK3r9I/mm4lV.vaHlUodCWQOUGv9paOHZa8gh/9MX4.It6cAH/
    shell: /bin/bash
    ssh_authorized_keys:
      - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC43t3iUh8uqWzajviRlEtIrrVPyEHHNFG2/Ne57/CwLq2ptqCN/VEG9OAmlkMTYkZU5AMAtpe3HYl1YsCgNLdxZlmaHVffGMPwaUxEYOtqyOMhqjJr95S8cfnZ/uQ6to+HwEPpxA3GOEURXU5ti5mpecwI2YKA4mvHwYjkDKq+bnLtSTg/+iQcTC/kX0efU4VIZ5tSDHiL8DuTzpS+g7euqLSaABQjMGJ0819bPs8zc/NP1Vx3oql2QrUuTrWcneYSqn71VvCIpjeAJ0j9PHWmlcL3rdc9NF0sk7ZCixhKvvHRdmCWWUTJ0Aaw66T7By+a3wwlhcY2/tpQHJltGBWVTRQS0eMit18DCOr5oLgf7xAQkZrWXCIRbbgxBY+hOFITkXM4vXyVfzYZ0WiBATp0UtKor+SR3MPcXkX8t+ok4IWvlxmB81E+NOFyKyw1ysDMwLPtOy2YiOdIWIWkPe6M2ih0BDPGxx5fSig7819Jo99gsrU6gc02zR8OUCuWy/M= demo@keygen
timezone: America/Toronto
write_files:
  - path: /etc/byobu/autolaunch
  - path: /etc/ssh/sshd_config.d/pubkey_only.conf
    content: |
      PasswordAuthentication no
      PubkeyAuthentication yes
  - path: /etc/ssh/sshd_config.d/alternate_port.conf
    content: |
      Port 27221
"""

if server is not None:
    yesno = input("Server already exists; delete it? (Must enter 'yes' in all caps, followed by ENTER key): ")
    if yesno != "YES":
        print("Bailing...")
        sys.exit(1)

    yesno = input("I know you hate this, but are you really sure? (Must enter 'YES' all lower case, followed by ENTER key): ")
    if yesno != 'yes':
        print("Bailing...")
        sys.exit(1)
    
    if conn.delete_server(server, True, 600):
        print("Server successfully deleted")
    else:
        print("Weird. Server doesn't exist. Bailing...")
        sys.exit(2)

server = conn.create_server(server_name, image=image, flavor=flavor, network=network, userdata=userdata, wait=True, timeout=600)

print("ip: {ip}".format(ip=server.accessIPv4))
