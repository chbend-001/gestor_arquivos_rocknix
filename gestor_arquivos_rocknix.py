#!/usr/bin/env python3
import sys
import os
import subprocess
import shutil
import time
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QWidget, QLabel, QProgressBar, QFileDialog, QTextEdit, 
                             QHBoxLayout, QDialog, QCheckBox, QScrollArea, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QRadioButton)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QPixmap

# --- Mapeamento Técnico de Sistemas ---
MAPA_EXTENSOES = {
    '.zip': 'arcade', '.7z': 'arcade',
    '.lst': 'naomi', '.dat': 'naomi', 
    '.neo': 'neogeo',
    '.nds': 'nds',
    '.3ds': 'n3ds', '.cia': 'n3ds',
    '.bin': 'psx', '.cue': 'psx', '.chd': 'psx', '.pbp': 'psx',
    '.iso': 'ps2', '.gdi': 'dreamcast',
    '.rvz': 'gc', '.nkit.iso': 'gc',
    '.3do': '3do', '.ccd': 'pcenginecd',
    '.cso': 'psp',
    '.nes': 'nes', '.sfc': 'snes', '.smc': 'snes', '.gba': 'gba', 
    '.gb': 'gb', '.gbc': 'gbc', '.md': 'megadrive', '.sms': 'mastersystem', 
    '.v64': 'n64', '.z64': 'n64', '.n64': 'n64', '.pce': 'pcengine'
}

SISTEMAS_PARA_CHD = ['psx', 'ps2', 'dreamcast', 'saturn', 'gc', 'naomi', 'atomiswave', 'psp']
SISTEMAS_DISPONIVEIS = sorted(list(set(MAPA_EXTENSOES.values())))

class ConfigDialog(QDialog):
    def __init__(self, compactar_lista):
        super().__init__()
        self.setWindowTitle("Configurações de Arquivos")
        self.setMinimumSize(350, 500)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Comprimir automaticamente ao enviar:</b>"))
        
        self.scroll = QScrollArea()
        self.container = QWidget()
        self.scroll_layout = QVBoxLayout(self.container)
        self.checks = {}
        for sys_name in SISTEMAS_DISPONIVEIS:
            cb = QCheckBox(sys_name.upper())
            cb.setChecked(sys_name in compactar_lista)
            self.checks[sys_name] = cb
            self.scroll_layout.addWidget(cb)
        
        self.scroll.setWidget(self.container)
        self.scroll_layout.addStretch() # Mantém os itens no topo
        self.scroll.setWidgetResizable(True)
        layout.addWidget(self.scroll)
        
        btn_save = QPushButton("Salvar Preferências")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)

class WorkerEnvio(QThread):
    log_sinal = pyqtSignal(str)
    progresso_sinal = pyqtSignal(int)
    concluido_sinal = pyqtSignal()

    def __init__(self, arquivos_selecionados, destino_path, compactar_lista):
        super().__init__()
        self.arquivos = arquivos_selecionados
        self.destino_path = Path(destino_path)
        self.compactar_lista = compactar_lista

    def run(self):
        total = len(self.arquivos)
        for i, arquivo_str in enumerate(self.arquivos):
            arquivo = Path(arquivo_str)
            ext = arquivo.suffix.lower()
            sistema = MAPA_EXTENSOES.get(ext, 'arcade')

            if ext in ['.lst', '.dat'] and "atomiswave" in str(arquivo).lower():
                sistema = 'atomiswave'

            pasta_final = self.destino_path / sistema
            pasta_final.mkdir(parents=True, exist_ok=True)

            try:
                if sistema in self.compactar_lista:
                    if sistema in SISTEMAS_PARA_CHD and ext in ['.cue', '.iso', '.gdi', '.lst', '.bin']:
                        self.log_sinal.emit(f"💿 Otimizando disco (CHD): {arquivo.name}")
                        saida = pasta_final / f"{arquivo.stem}.chd"
                        subprocess.run(["chdman", "createcd", "-i", str(arquivo), "-o", str(saida)], check=True, capture_output=True)
                    elif ext not in ['.zip', '.7z', '.chd', '.cso', '.cia']:
                        self.log_sinal.emit(f"📦 Comprimindo arquivo: {arquivo.name}")
                        saida = pasta_final / f"{arquivo.stem}.zip"
                        subprocess.run(["7z", "a", "-tzip", str(saida), str(arquivo)], stdout=subprocess.DEVNULL)
                    else:
                        shutil.copy2(arquivo, pasta_final / arquivo.name)
                else:
                    self.log_sinal.emit(f"➡️ Copiando original: {arquivo.name}")
                    shutil.copy2(arquivo, pasta_final / arquivo.name)
            except Exception as e:
                self.log_sinal.emit(f"⚠️ Erro no arquivo {arquivo.name}: {str(e)}")
            
            self.progresso_sinal.emit(int(((i + 1) / total) * 100))
        self.concluido_sinal.emit()

class RocknixGui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.compactar_lista = [s for s in SISTEMAS_DISPONIVEIS if s not in ['arcade', 'n3ds']]
        self.origem = None
        self.destino_sd = None
        self.setWindowTitle("Gestor de Arquivos ROCKNIX v1.9.1")
        self.setMinimumSize(950, 750)
        self.setStyleSheet("QMainWindow { background-color: #1e1e1e; color: #ffffff; }")
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)

        header = QHBoxLayout()
        mode_box = QVBoxLayout()
        self.rb_rede = QRadioButton("Rede (rocknix.local)")
        self.rb_sd = QRadioButton("SD Card / Pasta Manual")
        self.rb_rede.setChecked(True)
        mode_box.addWidget(QLabel("<b>Destino do Envio:</b>"))
        mode_box.addWidget(self.rb_rede)
        mode_box.addWidget(self.rb_sd)
        header.addLayout(mode_box)
        header.addStretch()
        
        self.btn_cfg = QPushButton("⚙️ Preferências de Compressão")
        self.btn_cfg.clicked.connect(self.abrir_cfg)
        header.addWidget(self.btn_cfg, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addLayout(header)

        self.tabela = QTableWidget(0, 3)
        self.tabela.setHorizontalHeaderLabels(["Enviar", "Nome do Arquivo", "Sistema"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela.setStyleSheet("background-color: #2d2d2d; color: white;")
        layout.addWidget(self.tabela)

        self.log_min = QTextEdit(readOnly=True)
        self.log_min.setMaximumHeight(100)
        self.log_min.setStyleSheet("background-color: black; color: #00ff00; font-family: monospace;")
        layout.addWidget(self.log_min)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        btns = QHBoxLayout()
        self.btn_sel_origem = QPushButton("📂 1. Selecionar Arquivos")
        self.btn_sel_origem.clicked.connect(self.scan_origem)
        self.btn_sel_sd = QPushButton("💾 2. Localizar SD")
        self.btn_sel_sd.clicked.connect(self.selecionar_sd)
        self.btn_sel_sd.setVisible(False)
        self.btn_go = QPushButton("🚀 3. Iniciar Envio")
        self.btn_go.setEnabled(False)
        self.btn_go.setStyleSheet("background: #28a745; color: white; font-weight: bold; height: 45px;")
        self.btn_go.clicked.connect(self.iniciar)

        self.rb_sd.toggled.connect(lambda: self.btn_sel_sd.setVisible(self.rb_sd.isChecked()))
        btns.addWidget(self.btn_sel_origem)
        btns.addWidget(self.btn_sel_sd)
        btns.addWidget(self.btn_go)
        layout.addLayout(btns)
        self.setCentralWidget(main_widget)

    def scan_origem(self):
        p = QFileDialog.getExistingDirectory(self, "Escolher Pasta de Origem")
        if p:
            self.origem = Path(p)
            self.tabela.setRowCount(0)
            arquivos = sorted([f for f in self.origem.iterdir() if f.suffix.lower() in MAPA_EXTENSOES])
            for f in arquivos:
                row = self.tabela.rowCount()
                self.tabela.insertRow(row)
                item = QTableWidgetItem(); item.setCheckState(Qt.CheckState.Checked)
                self.tabela.setItem(row, 0, item)
                self.tabela.setItem(row, 1, QTableWidgetItem(f.name))
                self.tabela.setItem(row, 2, QTableWidgetItem(MAPA_EXTENSOES[f.suffix.lower()].upper()))
            self.btn_go.setEnabled(True)
            self.log_min.append(f"✅ Encontrados {len(arquivos)} arquivos compatíveis.")

    def selecionar_sd(self):
        p = QFileDialog.getExistingDirectory(self, "Selecione a pasta ROMS no seu cartão")
        if p: self.destino_sd = p

    def abrir_cfg(self):
        dialog = ConfigDialog(self.compactar_lista)
        if dialog.exec():
            self.compactar_lista = [s for s, cb in dialog.checks.items() if cb.isChecked()]

    def iniciar(self):
        if self.rb_rede.isChecked():
            subprocess.run(["gio", "mount", "smb://rocknix.local/roms"], capture_output=True)
            time.sleep(1)
            uid = os.getuid()
            base_gvfs = Path(f"/run/user/{uid}/gvfs/")
            destino = next((p / "roms" for p in base_gvfs.iterdir() if "server=rocknix" in p.name.lower()), None)
        else:
            destino = Path(self.destino_sd) if self.destino_sd else None

        if not destino:
            self.log_min.append("❌ Erro: Destino não localizado (Verifique a rede ou o SD).")
            return

        selecionados = [str(self.origem / self.tabela.item(i, 1).text()) 
                        for i in range(self.tabela.rowCount()) 
                        if self.tabela.item(i, 0).checkState() == Qt.CheckState.Checked]

        self.btn_go.setEnabled(False)
        self.worker = WorkerEnvio(selecionados, destino, self.compactar_lista)
        self.worker.log_sinal.connect(self.log_min.append)
        self.worker.progresso_sinal.connect(self.progress.setValue)
        self.worker.concluido_sinal.connect(lambda: (self.btn_go.setEnabled(True), self.log_min.append("🎉 Envio finalizado!")))
        self.worker.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = RocknixGui(); w.show()
    sys.exit(app.exec())
