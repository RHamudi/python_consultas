# Automação de Consulta com SeleniumBase

## 📌 Requisitos

Antes de rodar o script, certifique-se de ter instalado:

- **Python** (versão 3.7 ou superior)
- **Google Chrome** (ou outro navegador compatível)
- **ChromeDriver** compatível com sua versão do navegador

## 🔧 Instalação

1. Clone o repositório ou baixe o arquivo `script.py`
2. Instale as dependências:

   ```sh
   pip install seleniumbase selenium pandas openpyxl
   ```

## Como usar

1. Coloque o arquivo excel no mesmo diretorio do final.py
2. O documento precisa ter a seguinte estrutura (CPF,Nome, Data Nascimento, Nome Mãe)
   3.Execute o script:

```sh
  python final.py
```

4.O script irá:

    Acessar o site
    Preencher os campos automaticamente
    Baixar os arquivos e organizá-los
    Salvar CPFs inválidos em cpfs_pulados.xlsx
