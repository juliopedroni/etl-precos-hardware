import os
import re
import requests
import psycopg2
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

N8N_WEBHOOK_URL = "http://localhost:5678/webhook-test/alerta-preco"


def extrair_dados(url):
    print("[1] Extraindo dados com Selenium...")
    options = webdriver.ChromeOptions()
    
    
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    
    try:
        titulo = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="productOverview"]/div[2]/div/div[1]/h1'))
        ).text
        
        preco = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="productMainWrapper"]/div[2]/div[2]/div/div[1]/div[2]/div/p/number-flow-react'))
        ).text
        
        return titulo, preco
    finally:
        driver.quit()


def transformar_dados(titulo_bruto, preco_bruto):
    print("[2] Limpando e formatando dados...")
    titulo_limpo = titulo_bruto.strip()
    preco_limpo = re.sub(r'[^\d,]', '', preco_bruto).replace(',', '.')
    return titulo_limpo, float(preco_limpo)


def salvar_e_verificar(nome, preco_atual, url):
    print("[3] Consultando histórico no PostgreSQL e inserindo nova coleta...")
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS")
    )
    cursor = conn.cursor()
    
   
    cursor.execute("""
        SELECT preco FROM historico_precos 
        WHERE produto_nome = %s 
        ORDER BY data_coleta DESC LIMIT 1
    """, (nome,))
    
    resultado = cursor.fetchone()
    preco_antigo = float(resultado[0]) if resultado else preco_atual
    
    
    cursor.execute("""
        INSERT INTO historico_precos (produto_nome, preco, url)
        VALUES (%s, %s, %s)
    """, (nome, preco_atual, url))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return preco_antigo

def disparar_alerta_n8n(nome, preco_atual, preco_antigo, link, forcar_teste=True):
    print("[4] Analisando regra de negócio e enviando Webhook...")
    
    if forcar_teste or preco_atual <= (preco_antigo * 0.85):
        print("🚨 Disparando requisição POST para o n8n...")
        
        payload = {
            "produto": nome,
            "preco_anterior": preco_antigo,
            "preco_atual": preco_atual,
            "desconto_percentual": 15.0 if forcar_teste else round(((preco_antigo - preco_atual) / preco_antigo) * 100, 1),
            "link": link
        }
        
        resposta = requests.post(N8N_WEBHOOK_URL, json=payload)
        
        if resposta.status_code == 200 or resposta.status_code == 201:
            print("✅ Sucesso! O payload JSON foi entregue ao n8n.")
        else:
            print(f"⚠️ n8n respondeu com o código HTTP: {resposta.status_code}")
    else:
        print("✅ Preço estável. Nenhum alerta necessário.")

if __name__ == "__main__":
    link = "https://www.kabum.com.br/produto/1029920/celular-samsung-galaxy-s26-ultra-sm-s948b-nfc-dual-sim-de-512gb-12gb-ram-de-6-9-200-50-10-50mp-12mp-preto"
    
    titulo_sujo, preco_sujo = extrair_dados(link)
    nome, preco_atual = transformar_dados(titulo_sujo, preco_sujo)
    preco_antigo = salvar_e_verificar(nome, preco_atual, link)
    

    disparar_alerta_n8n(nome, preco_atual, preco_antigo, link, forcar_teste=True)