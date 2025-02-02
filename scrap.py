from seleniumbase import Driver
from selenium.webdriver.common.by import By
from seleniumbase.common.exceptions import NoSuchElementException
import pandas as pd
import os
import time

driver = Driver(uc=True, headless=False)

url = "https://servicos.pf.gov.br/epol-sinic-publico/"
pasta_download = os.path.join(os.getcwd(), "downloaded_files")

driver.uc_open_with_reconnect(url, reconnect_time=6)

driver.uc_gui_click_captcha()

df = pd.read_excel("dados.xlsx", engine="openpyxl", dtype={'CPF': str})

cpfs_pulados = []
# df = pd.read_excel("dados.xlsx", engine="openpyxl")
# cpfs = df["CPF"].astype(str).tolist()
# nomes = df["Nome"].tolist()
# data_nascs = df["Data Nascimento"].astype(str).tolist()
# nome_maes = df["Nome Mãe"].tolist()

for index, row in df.iterrows():
    cpf = row["CPF"]  # Substitua "cpf" pelo nome da coluna no Excel
    nome = row["Nome"]  # Substitua "nome" pelo nome da coluna no Excel
    data_nasc = row["Data Nascimento"]  # Substitua "data_nasc" pelo nome da coluna no Excel
    nome_mae = row["Nome Mãe"]  # Substitua "nome_mae" pelo nome da coluna no Excel

    # Verificação de valores ausentes ou inválidos
    if not all([
        not pd.isna(cpf) and str(cpf).strip(),  # Verifica se cpf não é NaN e não está vazio
        not pd.isna(nome) and str(nome).strip(),  # Verifica se nome não é NaN e não está vazio
        not pd.isna(data_nasc) and str(data_nasc).strip(),  # Verifica se data_nasc não é NaN e não está vazio
        not pd.isna(nome_mae) and str(nome_mae).strip()  # Verifica se nome_mae não é NaN e não está vazio
    ]):
        cpfs_pulados.append([cpf, nome, data_nasc, nome_mae])
        driver.refresh()
        continue

    cpf = cpf
    nome = nome
    nacio = "Brasil"
    data_nasc = data_nasc
    nome_mae = nome_mae

    cpf_input = driver.find_element('pf-input-cpf input[type="text"]')
    cpf_input.send_keys(cpf)
    nome_input = driver.find_element('[formcontrolname="nome"]')
    nome_input.send_keys(nome)
    
    try:
        erro_cpf = driver.wait_for_element('span.p-confirm-dialog-message.ng-tns-c58-1', timeout=1)
        if "Formato do CPF inválido." in erro_cpf.text:
            cpfs_pulados.append([cpf, nome, data_nasc, nome_mae])
            driver.refresh()
            continue  # Sai do loop e passa para a próxima iteração
    except NoSuchElementException:
        # Se o elemento não for encontrado dentro de 3 segundos, o código continua normalmente
        pass
    

    local = driver.wait_for_element('.p-multiselect.p-component')

    local.click()
    driver.wait_for_element('.p-multiselect-filter.p-inputtext')

    driver.send_keys('.p-multiselect-filter.p-inputtext', nacio)
    driver.click('.p-checkbox-box')

    data_input = driver.find_element('.ng-tns-c64-8.pf-inputtext')
    if not isinstance(data_nasc, str):
        data_input.send_keys(data_nasc.strftime("%d/%m/%Y"))
    else:
        data_input.send_keys(data_nasc)

    nome_mae_input = driver.find_element('input[formcontrolname="nomeMae"]')
    nome_mae_input.send_keys(nome_mae)
    nome_mae_input.click()
    driver.click('#btn-emitir-cac')
    driver.click('#btn-fechar-modal')
    try:
        error_cac = driver.wait_for_element(By.XPATH, "//span[contains(text(), 'Dados (nome, nome da mãe ou data de nascimento) não conferem com o CPF informado.')]", timeout=1)
        cpfs_pulados.append([cpf, nome, data_nasc, nome_mae])
        driver.refresh()
        continue
    except NoSuchElementException:
        # Se o elemento não for encontrado dentro de 3 segundos, o código continua normalmente
        pass

    
    arquivos = os.listdir(f'{pasta_download}')
    arquivos = [os.path.join(pasta_download, f) for f in arquivos]
    arquivo_baixado = max(arquivos, key=os.path.getctime)
    nome_base, extensao = os.path.splitext(arquivo_baixado)
    pasta_certificados = os.path.join(pasta_download, "certificados")
    os.makedirs(pasta_certificados, exist_ok=True)
    novo_caminho = os.path.join(pasta_certificados, f"{nome}{extensao}")
    os.rename(arquivo_baixado, novo_caminho)
    time.sleep(3)
    driver.refresh()

if cpfs_pulados:
    df_pulados = pd.DataFrame(cpfs_pulados, columns=["CPF", "Nome", "Data Nascimento", "Nome Mãe"])
    df_pulados.to_excel("cpfs_pulados.xlsx", index=False)
    print(cpfs_pulados)
    print("CPFs pulados foram salvos em 'cpfs_pulados.xlsx'.")
else:
    print("Nenhum CPF foi pulado.")


# Fechar o navegador após completar todos os dados
time.sleep(60)
driver.quit()