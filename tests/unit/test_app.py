"""
🔴 RED: Testes da Interface Streamlit (UI) usando AppTest.
Escritos ANTES da implementação (TDD).
"""
import pytest
from streamlit.testing.v1 import AppTest


class TestAppUI:
    """Testes da interface principal do Streamlit."""

    def test_app_inicia_na_tela_de_login(self):
        """O app deve iniciar pedindo identificação, pois não há sessão."""
        at = AppTest.from_file("../../app.py")
        at.session_state["_test_mode"] = True
        at.run()
        
        assert not at.exception
        # Verifica se renderizou componentes de login
        # Assumindo que criaremos um title ou header
        assert any("Bolão" in header.value for header in at.header)
        assert any("Identificação" in subheader.value for subheader in at.subheader)
        
        # Verifica se os campos de input de login existem
        assert len(at.text_input) >= 1
        assert len(at.button) >= 1

    def test_login_telefone_vazio_mostra_erro(self):
        at = AppTest.from_file("../../app.py")
        at.session_state["_test_mode"] = True
        at.run()
        
        # Assumindo que o primeiro input é o de busca e o botão é 'Entrar'
        at.text_input[0].input("").run()
        at.button[0].click().run()
        
        # Verifica se mostrou mensagem de erro (warning, error)
        assert at.error or at.warning

    # Testes mais complexos requerem mock do repositório, o que no Streamlit 
    # AppTest pode ser feito injetando um mock no session_state antes de rodar.
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
