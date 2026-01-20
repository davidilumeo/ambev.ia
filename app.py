import streamlit as st
from datetime import datetime

# ----------------------------
# Page config (tamanho e título)
# ----------------------------
st.set_page_config(
    page_title="Ambev.ia",
    page_icon="💬",
    layout="wide",
)

# ----------------------------
# Perguntas pré-definidas (X / Twitter)
# ----------------------------
X_QUESTIONS = [
    "O jovem esta bebendo menos alcool? E cerveja?",
    "O consumidor associa luta a alguma marca de cerveja? Qual? Quais perfis demograficos e de interesse associam mais/menos?",
    "Scan no QR Code da tampinha de Brahma aumenta fidelidade/volume/frequencia?",
    "E verdade que as pessoas gostam mais de colocar limao na Coronita porque o sabor do limao fica mais concentrado?",
    "Quero entender melhor Eisenbahn. A marca esta em evolucao ou nao?",
]

# ----------------------------
# CSS (estilo ChatGPT-like)
# ----------------------------
st.markdown(
    """
    <style>
    /* ===== Fundo geral ===== */
    .stApp {
        background-color: #ffffff;
        color: #0f172a;
    }

    /* ===== Sidebar ===== */
    section[data-testid="stSidebar"] {
        background-color: #f9f9f9;
        border-right: 1px solid #e5e7eb;
    }

    /* ===== Títulos ===== */
    h1, h2, h3, h4 {
        color: #0f172a !important;
    }

    /* ===== Container do chat ===== */
    .chat-wrap {
        max-width: 900px;
        margin: 0 auto;
        padding: 16px 12px 96px 12px;
    }

    /* ===== Bolhas ===== */
    .bubble {
        padding: 12px 14px;
        border-radius: 14px;
        margin: 10px 0;
        line-height: 1.5;
        font-size: 15px;
        max-width: 85%;
        border: 1px solid #e5e7eb;
        white-space: pre-wrap;
        word-wrap: break-word;
        background-color: #ffffff;
    }

    .user {
        background-color: #f4f4f5;
        margin-left: auto;
    }

    .assistant {
        background-color: #ffffff;
        margin-right: auto;
    }

    /* ===== Label (Você / Assistente) ===== */
    .meta {
        font-size: 12px;
        color: #6b7280;
        margin-bottom: 4px;
    }

    /* ===== Input fixo ===== */
    .input-bar {
        position: fixed;
        bottom: 16px;
        left: 0;
        right: 0;
        z-index: 9999;
        display: flex;
        justify-content: center;
        pointer-events: none;
    }

    .input-inner {
        width: min(900px, 92vw);
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 10px 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        pointer-events: auto;
    }

    textarea {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border-radius: 10px !important;
        border: 1px solid #e5e7eb !important;
    }

    textarea::placeholder {
        color: #9ca3af !important;
    }

    /* ===== Botões ===== */
    .stButton>button {
        background-color: #f3f4f6 !important;
        color: #0f172a !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 10px !important;
    }

    .stButton>button:hover {
        background-color: #e5e7eb !important;
    }

    /* ===== Ajustes gerais ===== */
    .block-container {
        padding-top: 12px;
        padding-bottom: 0px;
    }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# Estado (chats / menu / envio pendente)
# ----------------------------
if "chats" not in st.session_state:
    st.session_state.chats = {
        "Novo chat": [
            {"role": "assistant", "content": "Oi! Esse é a IA da Ambev. 😊\n\nMe manda uma mensagem aí embaixo."}
        ]
    }
    st.session_state.active_chat = "Novo chat"

if "sidebar_section" not in st.session_state:
    st.session_state.sidebar_section = "chats"  # "chats" ou "x"

if "pending_user_message" not in st.session_state:
    st.session_state.pending_user_message = ""

def new_chat():
    name = f"Chat {len(st.session_state.chats)+1}"
    st.session_state.chats[name] = [
        {"role": "assistant", "content": "Começamos uma novo chat. Como posso ajudar?"}
    ]
    st.session_state.active_chat = name

def rename_chat(old, new):
    if not new or new.strip() == "":
        return
    if new in st.session_state.chats:
        return
    st.session_state.chats[new] = st.session_state.chats.pop(old)
    st.session_state.active_chat = new

# ----------------------------
# Sidebar (menu fixo + chats)
# ----------------------------
with st.sidebar:
    # Menu fixo
    colA, colB = st.columns(2)
    if st.session_state.sidebar_section == "chats":
        st.markdown("### Chats")
        st.button("➕ Novo chat", use_container_width=True, on_click=new_chat)

        st.markdown("---")
        for chat_name in list(st.session_state.chats.keys()):
            is_active = (chat_name == st.session_state.active_chat)
            label = f"👉 {chat_name}" if is_active else chat_name

            if st.button(label, key=f"chat_{chat_name}", use_container_width=True):
                st.session_state.active_chat = chat_name

    else:
        st.markdown("### X (Twitter)")
        st.caption("Clique em uma pergunta pronta para enviar ao chat, ou crie uma nova.")

        st.markdown("**Perguntas pré-definidas**")
        for i, q in enumerate(X_QUESTIONS, start=1):
            if st.button(f"{i}. {q}", key=f"xq_{i}", use_container_width=True):
                st.session_state.pending_user_message = q
                st.rerun()

        st.markdown("---")
        st.markdown("**Criar nova**")
        custom = st.text_area(
            "Nova pergunta",
            placeholder="Digite sua pergunta...",
            label_visibility="collapsed",
            height=100,
            key="x_custom_question"
        )
        if st.button("Enviar para o chat", use_container_width=True, key="x_send_custom"):
            if custom.strip():
                st.session_state.pending_user_message = custom.strip()
                st.session_state["x_custom_question"] = ""  # limpa a caixa
                st.rerun()

# ----------------------------
# Área principal
# ----------------------------
active = st.session_state.active_chat
messages = st.session_state.chats[active]

st.markdown(f"## {active}")

# ----------------------------
# Render das mensagens (bolhas)
# ----------------------------
st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)

for m in messages:
    role = m["role"]
    content = m["content"]

    who = "Você" if role == "user" else "Assistente"
    css_class = "user" if role == "user" else "assistant"
    meta = f'<div class="meta">{who} • {datetime.now().strftime("%H:%M")}</div>'

    st.markdown(
        f"""
        <div>
            {meta}
            <div class="bubble {css_class}">{content}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# Input fixo no rodapé
# ----------------------------

with st.form("chat_form", clear_on_submit=True):
    user_text = st.text_area("Mensagem", placeholder="Digite sua mensagem...", label_visibility="collapsed", height=70)
    col1, col2 = st.columns([6, 1])
    with col2:
        send = st.form_submit_button("Enviar")

st.markdown("</div></div>", unsafe_allow_html=True)

# ----------------------------
# "IA" de exemplo (placeholder)
# ----------------------------
def fake_assistant_reply(text: str) -> str:
    return (
        "✅ Recebi sua mensagem!\n\n"
        f"Você disse: **{text}**\n\n"
    )

# 1) Se veio algo do menu lateral (X/Twitter), injeta no chat
if st.session_state.pending_user_message.strip():
    injected = st.session_state.pending_user_message.strip()
    st.session_state.pending_user_message = ""
    st.session_state.chats[st.session_state.active_chat].append({"role": "user", "content": injected})
    st.session_state.chats[st.session_state.active_chat].append({"role": "assistant", "content": fake_assistant_reply(injected)})
    st.rerun()

# 2) Envio normal pelo input do rodapé
if send and user_text.strip():
    st.session_state.chats[st.session_state.active_chat].append({"role": "user", "content": user_text.strip()})
    st.session_state.chats[st.session_state.active_chat].append({"role": "assistant", "content": fake_assistant_reply(user_text.strip())})
    st.rerun()
