📦 Guia de Instalação Rápida

    Preparar o Ambiente: Certifique-se de que o seu sistema Linux possui as dependências listadas no arquivo requerimentos.txt:
    Bash

    sudo apt update && sudo apt install python3-pyqt6 mame-tools p7zip-full -y

    Organizar os Arquivos: Coloque o ficheiro de código rocknix_deployer_gui.py e a imagem icon.jpg na mesma pasta. O programa utiliza esta imagem como banner na interface.

    Executar: Dê permissão de execução ao ficheiro e inicie o gestor:
    Bash

    chmod +x rocknix_deployer_gui.py
    python3 rocknix_deployer_gui.py

📄 README.md (Versão v1.9.1)
Gestor de Arquivos ROCKNIX

O Gestor de Arquivos ROCKNIX é uma ferramenta utilitária desenvolvida para facilitar a transferência, organização e otimização de coleções de jogos para dispositivos que utilizam o sistema operativo ROCKNIX.

!
🚀 Funcionalidades Principais

    Identificação Inteligente: Reconhece automaticamente o sistema de destino com base na extensão do ficheiro.

    Otimização de Espaço: Converte ficheiros de disco (PS1, PS2, etc.) para o formato eficiente .chd e comprime cartuchos em .zip.

    Envio Flexível: Suporta o envio de ficheiros via Rede (SMB) ou diretamente para o Cartão SD.

    Interface Intuitiva: Permite selecionar individualmente quais ficheiros enviar através de uma tabela interativa.

🎮 Sistemas e Extensões Suportadas

O gestor está configurado para organizar os seguintes sistemas nas respetivas pastas do ROCKNIX:
Sistema	Extensões Reconhecidas	Pasta de Destino
Sega Naomi	.lst, .dat	/naomi
Nintendo 3DS	.3ds, .cia	/n3ds
Nintendo DS	.nds	/nds
Sony PSP	.cso, .iso	/psp
PlayStation 1	.bin, .cue, .chd, .pbp	/psx
Arcade	.zip, .7z	/arcade
Consolas Retro	.nes, .sfc, .gba, .md, etc.	Variável (conforme sistema)
🛠️ Requisitos Técnico

Para garantir que todas as funções de compressão e conversão funcionam corretamente, o sistema deve ter instalado:

    Python 3 com a biblioteca PyQt6.

    MAME Tools (para a ferramenta chdman).

    p7zip-full (para compressão de ficheiros).

📖 Como Utilizar

    Selecionar Arquivos: Clique no botão para escolher a pasta onde os seus jogos estão guardados no PC.

    Configurar Preferências (⚙️): Escolha quais os sistemas que devem sofrer compressão automática durante o envio.

    Escolher Destino: Defina se o envio será feito por rede ou para o Cartão SD.

    Iniciar Envio: Clique em "Iniciar Envio" e acompanhe o progresso na barra inferior.

Desenvolvido para a comunidade retrogamer.
