from tqdm import tqdm
import subprocess as sp
import json
import requests
import os

def getTopDownloads(url = 'https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.json'):
    '''
        Gets the top 5000 PyPi download packages. Expects JSON object from hugovk's github.

        Returns a list of packages.
    '''
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception("HTTP response is not 200!")

    try: 
        j = json.loads(r.text)
    except json.decoder.JSONDecodeError:
        raise Exception("JSON not found!")

    packages = []
    # download stats are stored in 'rows' variable
    for row in j['rows']:
        packages.append(row['project'])
    
    return packages

def initBasket():
    '''
        Initialises basket. Note that it changes the path based on the OS environment variable "BASKET_ROOT".
    '''
    if os.path.isdir(os.path.join(os.environ['HOME'], '.basket')):
        print(".basket already exists, deleting...")
        os.chdir(os.environ['HOME'])
        sp.run("rm -r .basket", shell=True)
    sp.run(["basket", "init"])
    return None

def downloadPackages(packages):
    '''
        Downloads packages specified as a list.
    '''
    if len(packages) == 0:
        raise Exception("List of packages is empty!")
    for p in tqdm(packages):
        run_command = ['basket', 'download']
        run_command.append(p)
        sp.run(run_command)
    return None

def getPackagesRequirements():
    '''
        Creates requirements.txt from package directory.
        Writes the requirements.txt file in package directory.
    '''
    r = sp.run(["basket", "list"], stdout=sp.PIPE)
    packages = r.stdout.decode('utf-8').split('\n')
    
    os.chdir(os.environ['HOME'])
    os.chdir('.basket')
    print("Generating requirements.txt ...")
    if os.path.isfile('requirements.txt'):
        print("requirements.txt already exists, deleting...")
        sp.run("rm requirements.txt", shell=True)
    file = open('requirements.txt', 'w')
    for p in packages:
        s = "==".join(p.split(" "))
        file.write(s+"\n")
    print("File generated!")
    return None

def scanPackages(path="requirements.txt"):
    '''
        Runs safety check on requirements.txt.
    '''
    os.chdir(os.environ['HOME'])
    os.chdir('.basket')
    sp.run(["safety", "check", "-r", path])
    return None

if __name__ == "__main__":
    packages = getTopDownloads()
    initBasket()
    downloadPackages(packages)
    getPackagesRequirements()
    scanPackages()


    
