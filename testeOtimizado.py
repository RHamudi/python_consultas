from seleniumbase import Driver
from selenium.webdriver.common.by import By
from seleniumbase.common.exceptions import NoSuchElementException
import pandas as pd
import os
import time

def iniciar_driver():
    return Driver(uc=True, headless=False)  # Modo headless para maior velocidade

url = "https://servicos.pf.gov.br/epol-sinic-publico/"
pasta_download = os.path.join(os.getcwd(), "downloaded_files")

df = pd.read_excel("dados.xlsx", engine="openpyxl", dtype={'CPF': str})
cpfs_pulados = []

# Configurações para acelerar o Selenium
driver = iniciar_driver()
driver.uc_open_with_reconnect(url, reconnect_time=3)  # Reduzir o tempo de reconexão
driver.uc_gui_click_captcha()

for index, row in df.iterrows():
    cpf = row["CPF"]
    nome = row["Nome"]
    data_nasc = row["Data Nascimento"]
    nome_mae = row["Nome Mãe"]

    # Verificação de valores ausentes ou inválidos
    if not all([
        not pd.isna(cpf) and str(cpf).strip(),
        not pd.isna(nome) and str(nome).strip(),
        not pd.isna(data_nasc) and str(data_nasc).strip(),
        not pd.isna(nome_mae) and str(nome_mae).strip()
    ]):
        cpfs_pulados.append([cpf, nome, data_nasc, nome_mae])
        continue

    try:
        # Preenche os campos do formulário
        cpf_input = driver.find_element('pf-input-cpf input[type="text"]')
        cpf_input.clear()
        cpf_input.send_keys(cpf)

        nome_input = driver.find_element('[formcontrolname="nome"]')
        nome_input.clear()
        nome_input.send_keys(nome)

        # Verifica se há erro de CPF inválido
        try:
            erro_cpf = driver.wait_for_element('span.p-confirm-dialog-message.ng-tns-c58-1', timeout=1)
            if "Formato do CPF inválido." in erro_cpf.text:
                cpfs_pulados.append([cpf, nome, data_nasc, nome_mae])
                continue
        except NoSuchElementException:
            pass

        # Preenche a nacionalidade
        local = driver.find_element('.p-multiselect.p-component')
        local.click()
        driver.find_element('.p-multiselect-filter.p-inputtext').send_keys("Brasil")
        driver.find_element('.p-checkbox-box').click()

        # Preenche a data de nascimento
        data_input = driver.find_element('.ng-tns-c64-8.pf-inputtext')
        data_input.clear()
        data_input.send_keys(data_nasc if isinstance(data_nasc, str) else data_nasc.strftime("%d/%m/%Y"))

        # Preenche o nome da mãe
        nome_mae_input = driver.find_element('input[formcontrolname="nomeMae"]')
        nome_mae_input.clear()
        nome_mae_input.send_keys(nome_mae)

        # Clica no botão de emitir
        driver.find_element('#btn-emitir-cac').click()
        driver.find_element('#btn-fechar-modal').click()

        # Verifica se há erro de dados não conferem
        try:
            error_cac = driver.wait_for_element(By.XPATH, "//span[contains(text(), 'Dados (nome, nome da mãe ou data de nascimento) não conferem com o CPF informado.')]", timeout=1)
            cpfs_pulados.append([cpf, nome, data_nasc, nome_mae])
        except NoSuchElementException:
            # Move o arquivo baixado para a pasta de certificados
            arquivos = os.listdir(pasta_download)
            arquivos = [os.path.join(pasta_download, f) for f in arquivos]
            arquivo_baixado = max(arquivos, key=os.path.getctime)
            pasta_certificados = os.path.join(pasta_download, "certificados")
            os.makedirs(pasta_certificados, exist_ok=True)
            os.rename(arquivo_baixado, os.path.join(pasta_certificados, f"{nome}{os.path.splitext(arquivo_baixado)[1]}"))

    except Exception as e:
        print(f"Erro ao processar {cpf}: {e}")
        cpfs_pulados.append([cpf, nome, data_nasc, nome_mae])

# Fecha o navegador ao final
driver.quit()

# Salva os CPFs pulados em um arquivo Excel
if cpfs_pulados:
    df_pulados = pd.DataFrame(cpfs_pulados, columns=["CPF", "Nome", "Data Nascimento", "Nome Mãe"])
    df_pulados.to_excel("cpfs_pulados.xlsx", index=False)
    print("CPFs pulados foram salvos em 'cpfs_pulados.xlsx'.")
else:
    print("Nenhum CPF foi pulado.")