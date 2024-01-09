import requests
import hashlib
import time
import re

# Replace these with your values
url_to_check = "https://shellshock.io/js/shellshock.js"

ping_roleid = "role id here"

stored_checksum = "stored_checksum.txt"
stored_version = "stored_version.txt"

webhook_publish_url = "url here"
webhook_log_url = "url here"

time_interval = 3600 #in seconds



def webhook_log(message):
    data = {
        "content": message
    }
    try:
        response = requests.post(webhook_log_url, json=data)
        print(message, response.status_code)
    except:
        print("no connection, wanted to send:",message)

def webhook_publish(message, file_content, file_name):
    data = {
        "content": message
    }
    if file_content:
        files = {'file': (file_name, file_content)}
        response = requests.post(webhook_publish_url, files=files, data=data)
    else:
        response = requests.post(webhook_publish_url, json=data)

    print(message, response.status_code)

def calculate_checksum(content):
    return hashlib.md5(content.encode()).hexdigest()

def read_stored_checksum():
    try:
        with open(stored_checksum, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return "checksum_undefined"

def write_checksum_to_file(checksum):
    with open(stored_checksum, "w") as file:
        file.write(checksum)

def read_stored_version():
    try:
        with open(stored_version, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return "0.0.0"

def write_version_to_file(version):
    with open(stored_version, "w") as file:
        file.write(version)

webhook_log("Startup")
while True:
    webhook_log("Looking for game update...")
    try:
        response = requests.get(url_to_check)
        current_checksum = calculate_checksum(response.text)
        checksum = read_stored_checksum()
        current_version = re.findall(r'"(\d+\.\d+\.\d+)",',response.text)[0]
        version = read_stored_version()

        if current_checksum != checksum:
            webhook_log("New version detected! Checksum: "+current_checksum+"; Version: "+current_version)
            write_checksum_to_file(current_checksum)
            write_version_to_file(current_version)
            webhook_publish("New version detected! Game updated, so StateFarm likely needs fixing: "+version+"->"+current_version, response.text,"shellshock_"+current_version+".js")
            webhook_publish("Checksum: "+current_checksum,False,False)
            webhook_publish("Dev Ping: <@&"+ping_roleid+">",False,False)
        else:
            webhook_log("No new version")

    except requests.RequestException as e:
        webhook_log(f"Error: {e}")

    webhook_log("Going into standby... next update in "+str(time_interval)+" seconds. Countdown: <t:"+str(time_interval+int(time.time()))+":R>")
    print("Standby...")
    time.sleep(time_interval)  # Sleep for an hour before checking again
