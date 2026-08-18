"""
Repositório de dados baseado no Google Sheets.

Implementa a interface BaseRepository utilizando a biblioteca gspread.
"""
import os
import json
import gspread
from typing import List, Optional
from dotenv import load_dotenv

from src.models.participante import Participante
from src.models.voto import Voto
from src.models.config_bolao import ConfigBolao
from src.repositories.base_repository import BaseRepository
from src.repositories.memory_repository import _normalizar_texto


class GoogleSheetsRepository(BaseRepository):
    """Repositório persistente no Google Sheets."""

    def __init__(self, credentials_path: str = "credentials.json"):
        load_dotenv("config.env")
        sheet_id = os.getenv("SheetID")
        if not sheet_id:
            raise ValueError("SheetID não encontrado no arquivo config.env")
            
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {credentials_path}")

        # Autentica e abre a planilha
        self._gc = gspread.service_account(filename=credentials_path)
        self._sh = self._gc.open_by_key(sheet_id)
        
        # Garante que as abas (worksheets) existam
        self._ws_config = self._ensure_worksheet("Configuracao", ["Chave", "Valor"])
        self._ws_participantes = self._ensure_worksheet(
            "Participantes", 
            ["Nome", "Telefone", "Status Voto", "Nivel de Acesso"]
        )
        self._ws_votos = self._ensure_worksheet(
            "Votos", 
            ["Telefone", "Dezenas Positivas", "Dezenas Negativas"]
        )
        
        # O gspread faz chamadas de rede lentas.
        # Numa aplicação real mais pesada faríamos cache, mas para MVP 
        # acessaremos a planilha a cada operação para garantir sincronia.

    def _ensure_worksheet(self, title: str, headers: List[str]) -> gspread.Worksheet:
        """Garante que uma aba existe e tem os cabeçalhos corretos."""
        try:
            ws = self._sh.worksheet(title)
        except gspread.exceptions.WorksheetNotFound:
            ws = self._sh.add_worksheet(title=title, rows=100, cols=10)
            
        # Verifica se os cabeçalhos estão preenchidos
        first_row = ws.row_values(1)
        if not first_row:
            ws.append_row(headers)
            
        return ws

    # --- Participantes ---

    def get_participantes(self) -> List[Participante]:
        registros = self._ws_participantes.get_all_records()
        participantes = []
        for r in registros:
            # Ignora linhas totalmente vazias
            if not any(r.values()):
                continue
            p = Participante(
                nome=str(r.get("Nome", "")),
                telefone_limpo=str(r.get("Telefone", "")),
                status_voto=str(r.get("Status Voto", "Pendente")),
                nivel_acesso=str(r.get("Nivel de Acesso", "Participante"))
            )
            participantes.append(p)
        return participantes

    def get_participante_by_telefone(self, telefone: str) -> Optional[Participante]:
        participantes = self.get_participantes()
        for p in participantes:
            if p.telefone_limpo == telefone:
                return p
        return None

    def get_participante_by_nome(self, nome: str) -> Optional[Participante]:
        nome_normalizado = _normalizar_texto(nome)
        participantes = self.get_participantes()
        for p in participantes:
            if _normalizar_texto(p.nome) == nome_normalizado:
                return p
        return None

    def add_participante(self, participante: Participante) -> None:
        existente = self.get_participante_by_telefone(participante.telefone_limpo)
        if existente is not None:
            raise ValueError(f"Telefone já cadastrado: {participante.telefone_limpo}")
            
        row = [
            participante.nome,
            participante.telefone_limpo,
            participante.status_voto,
            participante.nivel_acesso
        ]
        self._ws_participantes.append_row(row)

    def update_participante(self, participante: Participante) -> None:
        registros = self._ws_participantes.get_all_records()
        for idx, r in enumerate(registros):
            if str(r.get("Telefone", "")) == participante.telefone_limpo:
                # idx é 0-based. A linha na planilha é idx + 2 (1 pro cabeçalho, +1 pq sheets é 1-based)
                row_num = idx + 2
                self._ws_participantes.update(f"A{row_num}:D{row_num}", [[
                    participante.nome,
                    participante.telefone_limpo,
                    participante.status_voto,
                    participante.nivel_acesso
                ]])
                return
        raise ValueError(f"Participante com telefone {participante.telefone_limpo} não encontrado.")

    def update_participante_telefone(self, telefone_antigo: str, telefone_novo: str) -> None:
        registros = self._ws_participantes.get_all_records()
        for idx, r in enumerate(registros):
            if str(r.get("Telefone", "")) == telefone_antigo:
                row_num = idx + 2
                self._ws_participantes.update_cell(row_num, 2, telefone_novo) # Coluna B (2) = Telefone
                return
        raise ValueError(f"Participante com telefone {telefone_antigo} não encontrado.")

    # --- Votos ---

    def _parse_lista_inteiros(self, texto: str) -> List[int]:
        if not texto: return []
        try:
            return [int(x.strip()) for x in str(texto).split(",") if x.strip()]
        except ValueError:
            return []

    def get_votos(self) -> List[Voto]:
        registros = self._ws_votos.get_all_records()
        votos = []
        for r in registros:
            if not any(r.values()):
                continue
            telefone = str(r.get("Telefone", ""))
            pos = self._parse_lista_inteiros(r.get("Dezenas Positivas", ""))
            neg = self._parse_lista_inteiros(r.get("Dezenas Negativas", ""))
            votos.append(Voto(telefone, pos, neg))
        return votos

    def add_voto(self, voto: Voto) -> None:
        pos_str = ", ".join(map(str, voto.dezenas_positivas))
        neg_str = ", ".join(map(str, voto.dezenas_negativas))
        self._ws_votos.append_row([voto.telefone_limpo, pos_str, neg_str])

    def delete_voto(self, telefone: str) -> None:
        registros = self._ws_votos.get_all_records()
        # É mais seguro deletar de baixo para cima para não bagunçar os índices
        for idx in range(len(registros) - 1, -1, -1):
            if str(registros[idx].get("Telefone", "")) == telefone:
                row_num = idx + 2
                self._ws_votos.delete_rows(row_num)

    def contar_votos(self) -> int:
        # Pega a primeira coluna (Telefone) e conta, ignorando o cabeçalho
        col_valores = self._ws_votos.col_values(1)
        # Filtra strings vazias
        valores_validos = [v for v in col_valores[1:] if v.strip()]
        return len(valores_validos)

    # --- Configuração ---

    def _init_default_config(self):
        """Preenche a aba de configuração com os defaults caso esteja vazia."""
        # Se só tiver o cabeçalho
        if len(self._ws_config.get_all_values()) <= 1:
            self._ws_config.append_rows([
                ["quorum_alvo", "24"],
                ["status", "ABERTO"]
            ])

    def get_config(self) -> ConfigBolao:
        self._init_default_config()
        registros = self._ws_config.get_all_records()
        config_dict = {str(r.get("Chave", "")): str(r.get("Valor", "")) for r in registros if r.get("Chave")}
        
        quorum = int(config_dict.get("quorum_alvo", "24"))
        status = config_dict.get("status", "ABERTO")
        return ConfigBolao(quorum_alvo=quorum, status=status)

    def update_config(self, config: ConfigBolao) -> None:
        self._init_default_config()
        registros = self._ws_config.get_all_records()
        
        # Procura as chaves e atualiza
        for idx, r in enumerate(registros):
            chave = str(r.get("Chave", ""))
            row_num = idx + 2
            if chave == "quorum_alvo":
                self._ws_config.update_cell(row_num, 2, str(config.quorum_alvo))
            elif chave == "status":
                self._ws_config.update_cell(row_num, 2, config.status)
