"""
🔴 RED: Testes da Interface Streamlit (UI) usando AppTest.
Escritos ANTES da implementação (TDD).
"""
import pytest
from streamlit.testing.v1 import AppTest


class TestAppUI:
    """Testes da interface principal do Streamlit."""

    def test_app_inicia_na_tela_de_login(self):
        """Testa se o app renderiza os elementos básicos de login no início."""
        at = AppTest.from_file("../../app.py", default_timeout=10)
        at.run()
        
        # Verifica se renderizou o input de texto
        assert len(at.text_input) > 0
        # Verifica botão de Entrar (agora é "Acessar Bolão 🚀")
        assert any("Acessar" in btn.label for btn in at.button)
        
    def test_login_telefone_vazio_mostra_erro(self):
        """Verifica se exibe erro ao tentar logar sem digitar o telefone."""
        at = AppTest.from_file("../../app.py", default_timeout=10)
        at.run()
        
        # Encontra o botão e clica
        submit_btn = next(btn for btn in at.button if "Acessar" in btn.label)
        submit_btn.click()
        at.run()
        
        # Deve mostrar st.error
        assert len(at.error) > 0
        assert "identificação" in at.error[0].value.lower()
        
    def test_injetar_mock_repository(self):
        """Testa usar as variáveis de sessão para forçar estado de teste e simular login."""
        at = AppTest.from_file("../../app.py", default_timeout=10)
        # Pre-popula o state ANTES do run
        at.session_state["_test_mode"] = True
        at.run()
        
        # Simula login do João (que tem fone 11999998888 no mock)
        identificacao_input = at.text_input[0]
        identificacao_input.input("11999998888")
        
        submit_btn = next(btn for btn in at.button if "Acessar" in btn.label)
        submit_btn.click()
        at.run()
        
        # Agora ele não deve mais estar na tela de login, e sim na Cédula de Votação
        # E exibir Conectado como João (ignorando acentos para evitar erro no Windows)
        assert any("Conectado" in m.value for m in at.markdown)
