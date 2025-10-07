from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
from selenium import webdriver
import subprocess, time
import os

load_dotenv()

def kill_edge():
    try:
        subprocess.run(["taskkill", "/F", "/IM", "msedge.exe"],
                       check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
    time.sleep(3)

kill_edge()

driver_path = os.getenv("EDGE_DRIVER_PATH")
service = Service(driver_path)

options = webdriver.EdgeOptions()
options.use_chromium = True
options.add_argument(os.getenv("USER_DATA_PATH"))

driver = webdriver.Edge(service=service, options=options)
driver.get("https://web.whatsapp.com")
time.sleep(10)

grupo_nome = os.getenv("GRUPO_WHATS_MSG_GT")

search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
search_box.click()
search_box.send_keys(grupo_nome)
time.sleep(2)
search_box.send_keys(Keys.ENTER)

message_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
message_box.click()

mensagem = ':money\n:money\n Rotação GTzinha às 19:30 :money\n:money\n\n\nEK :shield\n:\nED :mask\n:\nShooter :gun\n:\nShooter :gun\n:\nQualquer vocação :person\n:\n'

for line in mensagem.split("\n"):
    message_box.send_keys(line)
    ActionChains(driver).key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()
message_box.send_keys(Keys.ENTER)

print("Mensagem enviada!")
time.sleep(10)

driver.quit()
