# What is PyserSSH

![Screenshot 2025-07-06 160010](https://github.com/user-attachments/assets/e530eeca-3331-4dec-beb8-7fc851ffdc4e)

This library will be **Pyserminal** (Python Server Terminal) as it supports multiple protocols such as ssh telnet rlogin and mores...

PyserSSH is a free and open-source Python library designed to facilitate the creation of customizable SSH terminal servers. Initially developed for research purposes to address the lack of suitable SSH server libraries in Python, PyserSSH provides a flexible and user-friendly solution for implementing SSH servers, making it easier for developers to handle user interactions and command processing.

The project was started by a solo developer to create a more accessible and flexible tool for managing SSH connections and commands. It offers a simplified API compared to other libraries, such as Paramiko, SSHim, and Twisted, which are either outdated or complex for new users.

This project is part from [damp11113-library](https://github.com/damp11113/damp11113-library)

## Some smail PyserSSH history
PyserSSH version [1.0](https://github.com/DPSoftware-Foundation/PyserSSH/releases/download/Legacy/PyserSSH10.py) (real filename is "test277.py") was created in 2023/9/3 for experimental purposes only. Because I couldn't find the best ssh server library for python and I started this project only for research. But I have time to develop this research into a real library for use. In software or server.

Read full history from [docs](https://damp11113.xyz/PyserSSHDocs/history.html)

# Install
Install from pypi
```bash
pip install PyserSSH
```
Install with [openRemoDesk](https://github.com/DPSoftware-Foundation/openRemoDesk) protocol
```bash
pip install PyserSSH[RemoDesk]
```
Install from Github
```bash
pip install git+https://github.com/damp11113/PyserSSH.git
```
Install from DPCloudev Git
```bash
pip install git+https://git.damp11113.xyz/DPSoftware-Foundation/PyserSSH.git
```

# Quick Example
This Server use port **2222** for default port
```py
from PyserSSH import Server, AccountManager

useraccount = AccountManager(allow_guest=True)
ssh = Server(useraccount)

@ssh.on_user("command")
def command(client, command: str):
    if command == "hello":
        client.send("world!")
        
ssh.run("your private key file")
```
This example you can connect with `ssh admin@localhost -p 2222` and press enter on login
If you input `hello` the response is `world`

# Demo
> [!WARNING]  
> For use in product please **generate new private key**! If you still use this demo private key maybe your product getting **hacked**! up to 90%. Please don't use this demo private key for real product.

https://github.com/damp11113/PyserSSH/assets/64675096/49bef3e2-3b15-4b64-b88e-3ca84a955de7

I intend to leaked private key because that key i generated new. I recommend to generate new key if you want to use on your host because that key is for demo only.
why i talk about this? because when i push private key into this repo in next 5 min++ i getting new email from GitGuardian. in that email say "
GitGuardian has detected the following RSA Private Key exposed within your GitHub account" i dont knows what is GitGuardian and i not install this app into my account.
