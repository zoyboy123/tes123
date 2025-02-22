import requests
import random
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote
import sys

access_token = "EAAAAUaZA8jlABO3fYp4NZCfBrVrplkvt3J6gSTnEgMjzTL4lmTiQYXr7ECaDHTOSJ7uAOgprR4mWLL6e3hx7xWkPIvCqK9ddf4qjxpnzU1jItqXHEmBNbIMz7jTNZAqhNirkWRszNUNe7BQZCn5yKZBsGCZAV0VzHY0cYMofZCzWeSE39B5iU2dJzCKe1C2ee0uGwZDZD"

page_ids = [
    "483796127570217", "1427879671479614", "445439625131124", "1014983000276634",
    "814702063422735", "3336244003296753", "355735168849587", "309451417507192",
    "1225772938071130", "1201585280184685", "3486907011625505", "742817531207577",
    "1107474864368796", "5111959598823492", "832838998355947", "1032255224537028",
    "762427382765677", "486770342102133", "1063690204017962", "240221658708735",
    "436465122218480", "7180350042063138", "802661721711774", "419776481874497",
    "1465353597126819", "668570691952295", "408005268874418", "1216109732756166",
    "2070344790026185", "1423354428069540", "430693699412373", "746800324041391",
    "252755851587428", "753444056693362", "326972620116965", "416535467217084",
    "830785608737485", "1566182330280525", "1520729928188963", "2135350230050899",
    "1610109999789603", "446661841724617"
]

messages = [
    "Hadir\nJangan Lupa Mampir Di status aku ya {%name%}",
    "Kontennya makin hari makin quality! Aku Bangga 😎 Jangan lupa balik dukungannya di Kontenku ya!\n#salam_intraksi",
]

target = 'Jaya & Edah'

def clear_line():
    sys.stdout.write("\033[K")

def countdown(sec):
    for remaining in range(sec, 0, -1):
        mins, secs = divmod(remaining, 60)
        timeformat = f"Menjalankan kembali dalam: {mins:02d}:{secs:02d}"
        print(timeformat, end="\r")
        time.sleep(1)
        clear_line()

def multi_get(urls):
    def fetch(url):
        try:
            return requests.get(url).json()
        except:
            return {}
    with ThreadPoolExecutor() as executor:
        return list(executor.map(fetch, urls))

def multi_post(urls):
    def post(url):
        try:
            return requests.post(url)
        except Exception as e:
            return e
    with ThreadPoolExecutor() as executor:
        return list(executor.map(post, urls))

def process_interactions():
    print("\nMemulai proses interaksi...")
    
    # Pilih halaman acak
    page_id = random.choice(page_ids)
    feed_url = f"https://graph.facebook.com/v21.0/{page_id}/feed"
    
    # Ambil postingan terbaru
    posts = requests.get(f"{feed_url}?fields=from&limit=3&access_token={access_token}").json()
    if 'data' not in posts:
        print("Gagal mengambil feed")
        return

    # Kumpulkan data status
    status_data = []
    for post in posts['data']:
        try:
            user_id = post['from']['id']
            user_name = post['from']['name']
            user_feed = requests.get(
                f"https://graph.facebook.com/{user_id}?fields=feed.limit(1)&access_token={access_token}"
            ).json()
            
            if user_feed.get('feed', {}).get('data'):
                status_id = user_feed['feed']['data'][0]['id']
                status_data.append({'name': user_name, 'status_id': status_id})
        except:
            continue

    # Cek komentar
    check_urls = [
        f"https://graph.facebook.com/{s['status_id']}?fields=comments.limit(100){{from{{name}}}}&access_token={access_token}"
        for s in status_data
    ]
    responses = multi_get(check_urls)

    # Filter yang perlu interaksi
    actions = []
    for i, res in enumerate(responses):
        if not any(c['from']['name'] == target for c in res.get('comments', {}).get('data', [])):
            actions.append(status_data[i])

    # Generate URL interaksi
    post_urls = []
    for a in actions:
        # Pilih pesan
        msg = random.choice(messages).replace('{%name%}', a['name'])
        
        # Tentukan salam
        current_time = time.gmtime(time.time() + 7*3600)
        hour = current_time.tm_hour
        if hour < 10:
            salam = f"Selamat Pagi {a['name']},"
        elif hour < 15:
            salam = f"Selamat Siang {a['name']},"
        elif hour < 18:
            salam = f"Selamat Sore {a['name']},"
        else:
            salam = f"Selamat Malam {a['name']},"
        
        full_msg = quote(f"{salam}\n{msg}")
        post_id = a['status_id']
        
        # Tambahkan URL komentar dan reaksi
        post_urls.extend([
            f"https://graph.facebook.com/{post_id}/comments?message={full_msg}&method=post&access_token={access_token}",
            f"https://graph.facebook.com/{post_id}/reactions?type={random.choice(['LIKE','LOVE','HAHA'])}&method=post&access_token={access_token}"
        ])

    # Eksekusi interaksi
    if post_urls:
        print(f"Menjalankan {len(post_urls)} interaksi...")
        results = multi_post(post_urls)
        
        # Tampilkan hasil
        success = 0
        for result in results:
            if isinstance(result, requests.Response) and result.status_code == 200:
                success += 1
        print(f"Berhasil: {success}/{len(post_urls)} interaksi")
    else:
        print("Tidak ada interaksi yang diperlukan")

if __name__ == "__main__":
    while True:
        process_interactions()
        countdown(300)  # 5 menit = 300 detik
