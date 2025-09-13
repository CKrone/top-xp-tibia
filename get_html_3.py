from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import unicodedata
import requests
import json
import math
import time
import os

# -------------------------------
# Funções auxiliares
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def path(filename):
    return os.path.join(BASE_DIR, filename)

def clean_text(text):
    """Remove espaços extras e caracteres não quebráveis"""
    return text.replace('\xa0', ' ').strip()

def normalize_name(name):
    """Remove acentos e coloca em minúsculas"""
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8')
    return name.strip().lower()

def parse_points(points_str):
    """Converte string com vírgulas em inteiro"""
    return int(points_str.replace(',', ''))

def format_xp(value: int) -> str:
    if value >= 1_000_000:  # milhão ou mais
        truncated = math.floor(value / 10_000) / 100   # divide, trunca e volta com 2 casas
        return f"{truncated:.2f}kk"
    elif value >= 1_000:  # mil ou mais
        truncated = math.floor(value / 10) / 100   # divide, trunca e volta com 2 casas
        return f"{truncated:.2f}k"
    else:
        return str(value)

# -------------------------------
# 1) Pegar membros da guild
# -------------------------------
url = "https://www.tibia.com/community/?subtopic=guilds&page=view"
payload = {"GuildName": "Abrigo de Mendigo"}
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.post(url, data=payload, headers=headers)
soup = BeautifulSoup(response.text, "lxml")
members = []

caption = soup.find("div", class_="Text", string="Guild Members")
if caption:
    container = caption.find_parent("div", class_="TableContainer")
    if container:
        guild_table = container.find("table", class_="TableContent")
        if guild_table:
            rows = guild_table.find_all("tr")[1:]
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 6:
                    rank = clean_text(cols[0].get_text(" ", strip=True))
                    if not rank:
                        rank = "Sem Rank"
                    name_and_title = clean_text(cols[1].get_text(" ", strip=True))
                    vocation = clean_text(cols[2].get_text(" ", strip=True))
                    level = clean_text(cols[3].get_text(" ", strip=True))
                    status = clean_text(cols[5].get_text(" ", strip=True))

                    members.append({
                        "rank": rank,
                        "name_and_title": name_and_title,
                        "vocation": vocation,
                        "level": int(level),
                        "status": status
                    })

# Criar set de nomes da guild normalizados
guild_member_names_normalized = set(normalize_name(m['name_and_title'].split(' (')[0]) for m in members)

# Salvar me-+*0mbros da guild em Excel
df_members = pd.DataFrame(members)
df_members.to_excel(path("guild_members.xlsx"), index=False)
print("Arquivo 'guild_members.xlsx' criado com sucesso!")

# -------------------------------
# 2) Pegar highscores
# -------------------------------
professions = {
    2: "Knight",
    3: "Paladin",
    4: "Sorcerer",
    5: "Druid",
    6: "Monk"
}

highscores = []
world = "Jadebra"

for prof_id, prof_name in professions.items():
    for page in range(1, 21):  # 20 páginas
        print("Executando página: ", page, " da vocação ", prof_name)
        url = f"https://www.tibia.com/community/?subtopic=highscores&world={world}&beprotection=-1&category=6&profession={prof_id}&currentpage={page}"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")

        table = soup.find("table", class_="TableContent")
        if not table:
            continue

        rows = table.find_all("tr")[1:]  # ignora header

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 6:
                continue

            name = clean_text(cols[1].get_text(" ", strip=True))
            # Normaliza o nome e filtra apenas membros da guild
            if normalize_name(name) not in guild_member_names_normalized:
                continue

            vocation = clean_text(cols[2].get_text(" ", strip=True))
            level = int(clean_text(cols[4].get_text(" ", strip=True)))
            points_str = clean_text(cols[5].get_text(" ", strip=True))
            points = parse_points(points_str)
            rank_in_highscore = int(clean_text(cols[0].get_text(" ", strip=True)))

            highscores.append({
                "name": name,
                "vocation": vocation,
                "level": level,
                "points": points,
                "profession": prof_name,
                "rank_in_highscore": rank_in_highscore
            })

        time.sleep(0.5)  # respeitar o servidor

# -------------------------------
# 3) Calcular XP ganho diário
# -------------------------------

# Arquivo histórico (com data)
yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y_%m_%d")
yesterday_file = path(f"guild_highscores_previous_{yesterday_str}.json")

# Carregar pontos do dia anterior se existir
if os.path.exists(yesterday_file):
    with open(yesterday_file, "r", encoding="utf-8") as f:
        prev_data = json.load(f)
    prev_points = {m['name']: m['points'] for m in prev_data}
else:
    prev_points = {}

for member in highscores:
    previous = prev_points.get(member['name'], 0)
    xp_gained = member['points'] - previous

    if xp_gained == member['points']:
        xp_gained = 0

    member['xp_gained'] = xp_gained

# Ordenar pelo XP ganho
highscores_sorted = sorted(highscores, key=lambda x: x['xp_gained'], reverse=True)

# Limitar top 20
top_20_highscores = highscores_sorted[:20]

# -------------------------------
# 4) Salvar resultados
# -------------------------------
today_str = datetime.now().strftime("%Y_%m_%d")
daily_file = path(f"guild_highscores_previous_{today_str}.json")

try:
    # Salva o arquivo histórico do dia
    with open(daily_file, "w", encoding="utf-8") as f:
        json.dump(highscores, f, ensure_ascii=False, indent=4)
    print(f"Arquivos '{daily_file}' salvo com sucesso!")
except Exception as e:
    print(f"Erro ao salvar os arquivos: {e}")

# Exibir JSON formatado
print(json.dumps(top_20_highscores, indent=4, ensure_ascii=False))

driver_path = r"C:\Users\Cristian\Desktop\edgeSel\msedgedriver.exe"
service = Service(driver_path)

# Configurações do Edge
options = webdriver.EdgeOptions()
options.use_chromium = True
options.add_argument(r"user-data-dir=C:\Users\Cristian\AppData\Local\Microsoft\Edge\User Data")

# Inicializa o driver
driver = webdriver.Edge(service=service, options=options)

# Abre WhatsApp Web
driver.get("https://web.whatsapp.com")
time.sleep(10)  # espera abrir o WhatsApp
# Nome do grupo ou contato
grupo_nome = "Abrigo de mendigos"

# Gera a mensagem automaticamente a partir do top 20
yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
mensagem = (
    f"Top 20 XP diário - Abrigo de Mendigo - {yesterday_str}\n\n"
)
for i, member in enumerate(top_20_highscores, start=1):
    xp_gained = format_xp(member['xp_gained'])
    mensagem += f"\u200b{i}. {member['name']} - Lv {member['level']} - {xp_gained}\n"

mensagem += f"\n_Última Atualização Tibia: 05:40_\n\n"

# Procurar o grupo pelo nome
search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
search_box.click()
search_box.send_keys(grupo_nome)
time.sleep(2)
search_box.send_keys(Keys.ENTER)

# Selecionar a caixa de texto da mensagem
message_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
message_box.click()
for line in mensagem.split("\n"):
    message_box.send_keys(line)
    ActionChains(driver).key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()
message_box.send_keys(Keys.ENTER)

print("Mensagem enviada!")
time.sleep(5)

# Fecha o navegador
driver.quit()
