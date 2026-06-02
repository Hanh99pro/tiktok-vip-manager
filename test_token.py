import requests

TOKEN = input("Nhap access token: ").strip()

url = "https://open.tiktokapis.com/v2/user/info/"

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

params = {
    "fields": "open_id,union_id,avatar_url,display_name"
}

r = requests.get(url, headers=headers, params=params)

print(r.status_code)
print(r.text)