# NameFluxer - Renomeador Inteligente de Arquivos

![Python Version](https://img.shields.io/badge/Python-3.x-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%2C%20macOS%2C%20Linux-lightgrey.svg)

---

## 📄 Sobre o NameFluxer

O **NameFluxer** é uma ferramenta de renomeação de arquivos em massa desenvolvida em Python com Tkinter. Ele oferece uma interface gráfica intuitiva para que usuários possam renomear facilmente grandes volumes de arquivos, aplicando padrões customizáveis, transformações de texto, numeração sequencial e manipulação de datas. Perfeito para organizar fotos, documentos, e qualquer outro tipo de arquivo!

---

## ✨ Recursos Principais

* **Renomeação em Massa**: Processa múltiplos arquivos de uma só vez.
* **Padrões de Nome Flexíveis**: Use placeholders como `{original_name}`, `{sequence}`, `{date}`, `{ext}` para criar nomes dinâmicos.
* **Numeração Sequencial**: Adicione números sequenciais personalizados (com início e dígitos configuráveis).
* **Data Personalizada**: Insira datas no nome dos arquivos, com opções de formato de entrada e saída.
* **Transformações de Texto**:
    * **Substituir Texto**: Encontre e substitua strings específicas.
    * **Remover Padrão (Regex)**: Utilize Expressões Regulares para remoção avançada de partes do nome.
    * **Conversão de Case**: Maiúsculas, minúsculas ou capitalização.
    * **Gerenciamento de Espaços**: Remover todos os espaços ou substituí-los por sublinhados.
* **Renomeação Recursiva**: Inclui arquivos em subpastas.
* **Tratamento de Conflitos**: Opção segura de adicionar sufixo incremental `(1), (2)` em caso de nomes duplicados (recomendado) ou sobrescrever arquivos (com aviso).
* **Prévia das Mudanças**: Visualize como os arquivos serão renomeados antes de aplicar as alterações.
* **Log de Operações**: Acompanhe o processo em tempo real no painel de log.
* **Interface Amigável**: GUI limpa e fácil de usar, com tooltips para guiar o usuário.
* **Tema Moderno**: Utiliza temas `ttkthemes` (Forest Light) e `azure-tcl-theme` para uma aparência mais moderna.

---

## 🚀 Como Usar

### 🖥️ Para Usuários (Versão Executável)

Se você tem o arquivo `NameFluxer.exe` (para Windows), siga estes passos:

1.  **Baixe o Executável**: Obtenha a versão mais recente do `NameFluxer.exe` [aqui](#) (link para download futuro).
2.  **Execute o Programa**: Dê um clique duplo no arquivo `NameFluxer.exe`.
3.  **Siga as Instruções**: Uma janela de boas-vindas aparecerá na primeira execução, e uma aba dedicada a "Instruções" está sempre disponível no aplicativo.

### 🐍 Para Desenvolvedores (Rodando do Código Fonte)

#### Pré-requisitos

Certifique-se de ter o Python 3.x instalado em seu sistema.

#### Instalação das Dependências

1.  **Clone o Repositório** (se aplicável, para futuros colaboradores):
    ```bash
    git clone [https://github.com/SeuUsuario/NameFluxer.git](https://github.com/SeuUsuario/NameFluxer.git)
    cd NameFluxer
    ```
2.  **Instale as Bibliotecas Necessárias**:
    ```bash
    pip install tkinter ttkthemes azure-tcl-theme
    ```
    *Obs: `tkinter` geralmente já vem com a instalação padrão do Python. `ttkthemes` e `azure-tcl-theme` são opcionais para temas visuais.*

#### Executando o Aplicativo

No diretório onde você salvou o arquivo `name_fluxer.py`, execute:

```bash
python name_fluxer.py

🛠️ Construindo o Executável (.exe) com PyInstaller
Se você deseja gerar o executável a partir do código-fonte:

Instale o PyInstaller:
Bash

pip install pyinstaller
Navegue até o Diretório do Script: Abra seu terminal/prompt de comando e vá para o diretório onde o arquivo name_fluxer.py está localizado.
Bash

cd /caminho/para/seu/projeto/NameFluxer
Execute o PyInstaller: Use o comando abaixo para criar um executável único e sem a janela do console:
Bash

pyinstaller --onefile --windowed --name NameFluxer --icon=seu_icone.ico name_fluxer.py
Substitua seu_icone.ico pelo caminho para um arquivo de ícone .ico se desejar um ícone personalizado. Caso contrário, remova --icon=seu_icone.ico.
Encontre o Executável: O executável NameFluxer.exe será criado na pasta dist/ dentro do seu diretório de projeto.
🤝 Contribuição
Contribuições são sempre bem-vindas! Se você tiver ideias para melhorias, encontrar bugs ou quiser adicionar novos recursos, por favor:

Faça um fork do repositório.
Crie uma nova branch (git checkout -b feature/sua-feature).
Faça suas alterações e commit (git commit -m 'Adiciona nova feature').
Envie para a branch original (git push origin feature/sua-feature).
Abra um Pull Request.
🐞 Reportando Problemas
Se você encontrar algum bug ou tiver sugestões, por favor, abra uma issue no GitHub Issues.

📜 Licença
Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para mais detalhes.

📞 Contato
Para dúvidas ou informações adicionais, você pode entrar em contato com Vinicius Silva - vinicius.cloudfy@gmail.com

