"""
Ponto de entrada da aplicação Streamlit.

Gerencia o estado da sessão e o roteamento entre as telas de Login,
Votação e Painel Admin.
"""
import streamlit as st

from src.repositories.memory_repository import MemoryRepository
from src.services.auth_service import AuthService
from src.services.votacao_service import VotacaoService
from src.services.engine_service import EngineService
from src.models.participante import Participante
from src.models.voto import Voto

from src.repositories.google_sheets_repository import GoogleSheetsRepository

# Configuração da página (deve ser a primeira chamada Streamlit)
st.set_page_config(
    page_title="Bolão Lotofácil",
    page_icon="🍀",
    layout="centered"
)


def injetar_css():
    st.markdown("""
    <style>
    /* Ocultar o menu hamburguer padrão e rodapé do Streamlit para visual mais limpo */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Arredondamento de botões */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        transform: scale(1.02);
    }
    
    /* Inputs com cantos arredondados */
    .stTextInput>div>div>input {
        border-radius: 8px;
    }
    
    /* Layout espaçado para cabeçalhos (estilo Airbnb) */
    h1, h2, h3 {
        font-weight: 800;
        letter-spacing: -0.02em;
    }
    </style>
    """, unsafe_allow_html=True)

# Aplica o CSS globalmente
injetar_css()

def inicializar_estado():
    """Inicializa as variáveis de sessão (Session State)."""
    if "repo" not in st.session_state:
        # Se for teste, usa memória e popula o repo com dados falsos
        if st.session_state.get("_test_mode", False):
            repo = MemoryRepository()
            repo.add_participante(Participante("João Silva", "11999998888", "Pendente", "Participante"))
            repo.add_participante(Participante("Admin", "00000000000", "Pendente", "Admin"))
        else:
            try:
                repo = GoogleSheetsRepository()
            except Exception as e:
                st.error(f"Erro ao conectar ao Google Sheets: {e}")
                st.stop()
            
        st.session_state["repo"] = repo

    if "auth_service" not in st.session_state:
        st.session_state["auth_service"] = AuthService(st.session_state["repo"])
        
    if "votacao_service" not in st.session_state:
        st.session_state["votacao_service"] = VotacaoService(st.session_state["repo"])
        
    if "engine_service" not in st.session_state:
        st.session_state["engine_service"] = EngineService()

    if "usuario_logado" not in st.session_state:
        st.session_state["usuario_logado"] = None


def render_login():
    """Renderiza a tela de login."""
    repo = st.session_state["repo"]
    config = repo.get_config()
    
    # Usa o nome do bolão configurado no Google Sheets
    st.header(f"🍀 {config.nome_bolao}")
    st.subheader("Identificação")
    
    if config.login_telefone_habilitado:
        st.markdown("Bem-vindo! Por favor, identifique-se usando seu **telefone** ou **nome completo**.")
        identificacao = st.text_input("Telefone ou Nome:")
    else:
        st.markdown("Bem-vindo! Por favor, identifique-se usando seu **Nome Completo**.")
        identificacao = st.text_input("Nome Completo:")
    
    if st.button("Entrar"):
        if not identificacao:
            st.error("Por favor, digite sua identificação.")
            return
            
        auth: AuthService = st.session_state["auth_service"]
        
        resultado = None
        if config.login_telefone_habilitado:
            tem_numeros = any(c.isdigit() for c in identificacao)
            if tem_numeros:
                resultado = auth.login_por_telefone(identificacao)
                if not resultado.sucesso and "não cadastrado" in resultado.mensagem.lower():
                    resultado_nome = auth.login_por_nome(identificacao)
                    if resultado_nome.sucesso or "já votou" in resultado_nome.mensagem.lower():
                        resultado = resultado_nome
                        
        # Se não tentou por telefone ou falhou, tenta por nome
        if resultado is None or (not resultado.sucesso and "telefone" in resultado.mensagem.lower()):
            resultado = auth.login_por_nome(identificacao)
            
        if resultado.sucesso:
            st.session_state["usuario_logado"] = resultado.participante
            st.success(resultado.mensagem)
            st.rerun()
        else:
            if "já votou" in resultado.mensagem.lower():
                st.warning(resultado.mensagem)
            else:
                st.error(resultado.mensagem)


def render_votacao():
    """Renderiza a cédula de votação."""
    usuario: Participante = st.session_state["usuario_logado"]
    
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.header("Cédula de Votação")
        st.markdown(f"👤 Conectado como: **{usuario.nome}**")
    with col2:
        if st.button("Sair"):
            st.session_state["usuario_logado"] = None
            st.rerun()
            
    if usuario.ja_votou():
        st.success("✅ Você já registrou seu voto! Aguarde o encerramento do bolão.")
        return
        
    st.subheader("Escolha suas dezenas")
    st.markdown("Regras: 1 a 5 favoritas, 0 a 3 indesejadas. Não pode haver interseção.")
    
    dezenas = list(range(1, 26))
    
    positivas = st.multiselect(
        "Dezenas Favoritas (+1 ponto)", 
        options=dezenas,
        max_selections=5,
        help="Escolha de 1 a 5 dezenas que você quer muito que estejam nos jogos."
    )
    
    # As dezenas escolhidas nas positivas não podem ser escolhidas nas negativas
    dezenas_disponiveis_neg = [d for d in dezenas if d not in positivas]
    
    negativas = st.multiselect(
        "Dezenas Indesejadas (-1 ponto)", 
        options=dezenas_disponiveis_neg,
        max_selections=3,
        help="Escolha de 0 a 3 dezenas que você prefere que fiquem de fora."
    )
    
    if st.button("Confirmar Voto", type="primary"):
        votacao: VotacaoService = st.session_state["votacao_service"]
        resultado = votacao.registrar_voto(
            telefone_limpo=usuario.telefone_limpo,
            dezenas_positivas=positivas,
            dezenas_negativas=negativas
        )
        
        if resultado.sucesso:
            st.success("Voto registrado com sucesso!")
            # Atualiza o estado do usuário logado na sessão para refletir que ele votou
            repo = st.session_state["repo"]
            st.session_state["usuario_logado"] = repo.get_participante_by_telefone(usuario.telefone_limpo)
            st.rerun()
        else:
            st.error(resultado.mensagem)


def render_admin():
    """Renderiza o painel de administração."""
    usuario: Participante = st.session_state["usuario_logado"]
    repo: MemoryRepository = st.session_state["repo"]
    engine: EngineService = st.session_state["engine_service"]
    config = repo.get_config()
    
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.header("Painel de Administração")
        st.markdown(f"👑 Bem-vindo, **{usuario.nome}**")
    with col2:
        if st.button("Sair"):
            st.session_state["usuario_logado"] = None
            st.rerun()
            
    st.divider()
    
    # Status e Métricas
    total_votos = repo.contar_votos()
    st.metric("Total de Votos Registrados", f"{total_votos} / {config.quorum_alvo}")
    
    st.markdown(f"Status do Bolão: **{config.status}**")
    
    if config.esta_aberto():
        st.warning("O bolão ainda está aberto para votação.")
        if st.button("Encerrar Votação Manualmente", type="secondary"):
            config.status = "FECHADO"
            repo.update_config(config)
            st.rerun()
    else:
        st.success("O bolão está fechado para novos votos. Pronto para gerar os jogos!")
        
        if st.button("Reabrir Votação", type="secondary"):
            config.status = "ABERTO"
            repo.update_config(config)
            st.rerun()
            
        st.subheader("Configurações de Geração")
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            qtd_jogos = st.number_input("Quantidade de Jogos", min_value=1, max_value=100, value=9)
        with col_q2:
            dezenas_por_jogo = st.number_input("Dezenas por Jogo", min_value=15, max_value=20, value=16)
        
        if st.button("🚀 Gerar Jogos (Motor Matemático)", type="primary"):
            with st.spinner("Analisando votos e calculando ranking..."):
                votos = repo.get_votos()
                ranking = engine.calcular_ranking(votos)
                
            with st.spinner("Gerando seed guloso e otimizando com SA (pode demorar alguns segundos)..."):
                # Geração com parâmetros configuráveis
                seed = engine.gerar_seed_guloso(ranking, qtd_jogos=int(qtd_jogos), dezenas_por_jogo=int(dezenas_por_jogo))
                # Otimização rápida na UI (1000 iterações)
                jogos = engine.otimizar_jogos(seed, ranking, iteracoes=1000)
                
                st.session_state["jogos_gerados"] = jogos
                st.session_state["ranking"] = ranking
                
        # Mostrar os jogos gerados
        if "jogos_gerados" in st.session_state:
            st.subheader("Resultados - Jogos Otimizados")
            jogos = st.session_state["jogos_gerados"]
            
            for i, jogo in enumerate(jogos):
                st.write(f"**Jogo {i+1}**: {jogo}")
                
            # Ranking Top 5 e Bottom 5 para contexto
            ranking = st.session_state["ranking"]
            top_5 = [d for d, _ in ranking[:5]]
            st.write(f"Top 5 dezenas mais votadas: {top_5}")
            
            # Exportação COLOGA
            st.divider()
            st.subheader("Exportação")
            
            # Formata os jogos para o padrão COLOGA: números com 2 dígitos separados por espaço
            linhas_cologa = []
            for jogo in jogos:
                linha = " ".join([f"{d:02d}" for d in jogo])
                linhas_cologa.append(linha)
            conteudo_cologa = "\n".join(linhas_cologa)
            
            st.download_button(
                label="📥 Baixar Arquivo para COLOGA (.txt)",
                data=conteudo_cologa,
                file_name="jogos_bolao_cologa.txt",
                mime="text/plain",
                type="primary"
            )


def main():
    inicializar_estado()
    
    usuario: Participante = st.session_state["usuario_logado"]
    
    if usuario is None:
        render_login()
    elif usuario.eh_admin():
        render_admin()
    else:
        render_votacao()


if __name__ == "__main__":
    main()
