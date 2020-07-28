import requests
sample = {'upload_file':open('link.txt','rb')}
r = requests.post('http://127.0.0.1:5000/automated_testing', files=sample)
print(r.content)