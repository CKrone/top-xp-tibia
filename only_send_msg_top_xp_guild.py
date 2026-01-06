from dotenv import load_dotenv
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium import webdriver
from datetime import datetime, timedelta
import json
import math
import time
import os

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORICO_DIR = os.path.join(BASE_DIR, "Historico")

def path(filename):
    return os.path.join(HISTORICO_DIR, filename)

def format_xp(value: int) -> str:
    if value >= 1_000_000:
        truncated = math.floor(value / 10_000) / 100
        return f"{truncated:.2f}kk"
    elif value >= 1_000:
        truncated = math.floor(value / 10) / 100
        return f"{truncated:.2f}k"
    else:
        return str(value)

today = datetime.now()
date_str_file = today.strftime("%Y_%m_%d")
date_str_msg = today.strftime("%d/%m/%Y")

file_path = path(f"guild_highscores_previous_{date_str_file}.json")

if not os.path.exists(file_path):
    raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

highscores_sorted = sorted(
    data,
    key=lambda x: x.get("xp_gained", 0),
    reverse=True
)

top_20 = highscores_sorted[:20]

total_xp_guild = sum(m.get("xp_gained", 0) for m in top_20)
yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
mensagem = (
    f"Top 20 XP diário - Abrigo de Mendigo - {yesterday_str}\n\n"
)

for i, member in enumerate(top_20, start=1):
    mensagem += (
        f"\u200b{i}. {member['name']} - "
        f"Lv {member['level']} - "
        f"{format_xp(member['xp_gained'])}\n"
    )

mensagem += f"\nTotal XP Guild: {format_xp(total_xp_guild)}\n"
mensagem += f"\n_Última Atualização Tibia: 05:40_\n\n"

driver_path = os.getenv("EDGE_DRIVER_PATH")
grupo_nome = os.getenv("GRUPO_WHATS_MSG_TOP_XP")

service = Service(driver_path)

options = webdriver.EdgeOptions()
options.use_chromium = True
options.add_argument(os.getenv("USER_DATA_PATH"))

driver = webdriver.Edge(service=service, options=options)

driver.get("https://web.whatsapp.com")
time.sleep(40)

search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
search_box.click()
search_box.send_keys(grupo_nome)
time.sleep(2)
search_box.send_keys(Keys.ENTER)

message_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
message_box.click()

for line in mensagem.split("\n"):
    message_box.send_keys(line)
    ActionChains(driver).key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()

message_box.send_keys(Keys.ENTER)

print("Mensagem enviada com sucesso!")

time.sleep(10)
driver.quit()
