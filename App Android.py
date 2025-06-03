import requests
import re

url = "https://drive.usercontent.google.com/download?id=1eHC2yNgBkh0TGepsxa27iAr97kry2ViI&export=download&authuser=2&confirm=t&uuid=76420d22-308d-4662-a5cd-64f2c8f0f3d3&at=ALoNOglvphjbSdMF29L-4EdOr6hy:1748956524850"

response = requests.get(url, stream=True)

if response.status_code == 200:
    content_disposition = response.headers.get('content-disposition')
    filename = "downloaded_file"
    
    if content_disposition:
        fname_match = re.findall('filename="?([^"]+)"?', content_disposition)
        if fname_match:
            filename = fname_match[0]
    
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)
    print(f"ดาวน์โหลดสำเร็จ: {filename}")
else:
    print(f"ล้มเหลวในการดาวน์โหลด (รหัส: {response.status_code})")
