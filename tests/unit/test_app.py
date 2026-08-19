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
        at = AppTest.from_file("../../app.py")
        # Injeta uma flag para o app usar o MemoryRepository com dados mock
        at.session_state["_test_mode"] = True
        at.run()
        
        # Agora tentamos fazer login com o usuário mock 'João Silva'
        # Assumimos que o app.py irá popular o repositório em _test_mode
        at.text_input[0].input("João Silva").run()
        at.button[0].click().run()
        
        assert not at.exception
        # Após st.rerun(), a tela de votação deve aparecer
        # Verificamos se 'Conectado como' está em algum markdown, evitando problemas de encoding com acentos
        assert any("Conectado como" in m.value for m in at.markdown)
