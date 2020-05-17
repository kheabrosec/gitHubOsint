import requests
import json
from bs4 import BeautifulSoup
import re
import argparse

def public_profile(username,v):
    url = "https://api.github.com/users/"+username+"/events/public"
    req = requests.get(url)
    j = json.loads(req.text)
    emails = []
    if str(j) == "{'message': 'Not Found', 'documentation_url': 'https://developer.github.com/v3/activity/events/#list-public-events-performed-by-a-user'}":
        if v==1:
            print("[X] Sorry, but can not retrieve info of user: "+username+" does not exists.")
        exit()
    else:
        for element in j:
            try:
                for commit in element["payload"]["commits"]:
                    if commit["author"]["email"] not in emails:
                        emails.append(commit["author"]["email"])
            except Exception as e:
                pass
    return emails

def get_proyects(username):
    url = "https://github.com/"+username+"?tab=repositories"
    req = requests.get(url)
    html1 = req.text
    proyects = []
    soup = BeautifulSoup(html1, "html.parser")
    for s in soup.find_all("a"):
        if re.findall("/"+username+"/",str(s)) and not re.findall("@",str(s)):
            s=str(s)
            for p in s.split(" "):
                try:
                    href=p.split("=")
                    if href[0] == "href":
                        proyect = href[1].split("\\")[0].strip('"')
                        proyects.append(proyect)
                except:
                    pass
    return proyects

def get_commits(proyect,v):
    url = "https://github.com{}/commits/".format(proyect)
    url = url.strip('"<>')
    req = requests.get(url)
    html1 = req.text
    commits = []
    soup = BeautifulSoup(html1, "html.parser")
    for s in soup.find_all("a"):
        if re.findall("https://github.com{}/commit/".format(proyect),str(s)):
            if v==1:
                print("Searching url: {}".format(proyect).strip('"<>'), end="\r")
            s=str(s)
            for p in s.split(" "):
                try:
                    href=p.split("=")
                    if href[0] == "href":
                        commit = href[1].split('">')[0].strip('"')
                        commits.append(commit)
                except:
                    pass
    return commits

def commit_profile(username,emails,v):
    commits = []
    for proyect in get_proyects(username):
        commits.append(get_commits(proyect,v))
    for commit in commits:
        for url in commit:
            req = requests.get(url+".patch")
            text = str(req.content).split("\\n")
            for line in text:
                line = line.split(" ")
                if line[0] == "From:":
                    if line[len(line)-1].strip("<>") not in emails:
                        emails.append(line[len(line)-1].strip("<>"))
                        break
    return emails

def printMain(username):
    print("Welcome to GitOSINT Tool!")
    emails=[]
    print("Searching in public profile...")
    emails=public_profile(username,1)
    if emails == []:
        print("[X] No emails found in public profile. \n")
    else:
        for email in emails:
            print("[✓] Email found: " + email)
    print("Searching in commits...")
    emails=commit_profile(str(username),emails,1)
    if emails == []:
        print("[X] No emails found in commits. \n")
    else:
        for email in emails:
            print("[✓] Email found: " + email)

def main(username,path):
    emails=[]
    emails=public_profile(username,0)
    emails=commit_profile(str(username),emails,0)
    print("Saving in to: "+path)
    j = {"user": username,"emails": emails}
    with open(path,"w+") as f:
        json.dump(j,f)


if __name__=='__main__':
    try:
        parser = argparse.ArgumentParser(description='Python tool to collect emails from github users.')
        parser.add_argument('-n', '--name', help='GitHub Username', required=True)
        parser.add_argument('-o', '--output', help='Output type.',choices=["json","cli"],default="cli")
        parser.add_argument('-p', '--path', help='Output path.', default="")
        args = vars(parser.parse_args())
        username=args["name"]
        if args["output"]=="json":
            if args["path"] == "":
                path = username+".txt"
            else:
                path = args["path"]
            main(username,path)
        else:
            printMain(username)
    except KeyboardInterrupt:
        exit(1)
