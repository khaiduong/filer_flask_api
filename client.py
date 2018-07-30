import requests
import os
url = "http://localhost:8000/"
filename = '/tmp/output.txt'
#files = {'file': fin}
if os.path.exists(filename):
    fin = open(filename, 'rb')
    files = {'file': fin}
    try:
        r = requests.post(url, files=files)
        print r.text
    finally:
        fin.close()
else:
    print "File does not exist"

