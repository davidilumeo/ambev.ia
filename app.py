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
# Helpers (ordem e nome automático)
# ----------------------------
def _title_from_text(text: str, max_len: int = 28) -> str:
    t = " ".join((text or "").strip().split())
    if not t:
        return "Novo chat"
    t = t[:max_len].strip()
    return t

def _unique_chat_name(base: str) -> str:
    name = base
    i = 2
    while name in st.session_state.chats:
        name = f"{base} ({i})"
        i += 1
    return name

def bump_chat_to_top(chat_name: str):
    if "chat_order" not in st.session_state:
        st.session_state.chat_order = list(st.session_state.chats.keys())
    if chat_name in st.session_state.chat_order:
        st.session_state.chat_order.remove(chat_name)
    st.session_state.chat_order.insert(0, chat_name)

def rename_chat(old, new):
    new = (new or "").strip()
    if not new:
        return
    if new in st.session_state.chats:
        return

    st.session_state.chats[new] = st.session_state.chats.pop(old)

    if "chat_order" in st.session_state and old in st.session_state.chat_order:
        idx = st.session_state.chat_order.index(old)
        st.session_state.chat_order[idx] = new

    st.session_state.active_chat = new

def maybe_autoname_chat(chat_name: str, user_text: str) -> str:
    is_generic = chat_name == "Novo chat" or chat_name.startswith("Chat ")
    if not is_generic:
        return chat_name

    base = _title_from_text(user_text)
    new_name = _unique_chat_name(base)

    if new_name != chat_name:
        rename_chat(chat_name, new_name)
        return new_name

    return chat_name

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

    /* ===== Ocultar toolbar/header do Streamlit (Share etc.) ===== */
    div[data-testid="stToolbar"] { display: none !important; }
    div[data-testid="stToolbarActions"] { display: none !important; }
    .stAppToolbar { display: none !important; }
    header[data-testid="stHeader"] { display: none !important; }
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
    st.session_state.chat_order = ["Novo chat"]

if "chat_order" not in st.session_state:
    st.session_state.chat_order = list(st.session_state.chats.keys())

if "sidebar_section" not in st.session_state:
    st.session_state.sidebar_section = "chats"  # "chats" ou "x"

if "pending_user_message" not in st.session_state:
    st.session_state.pending_user_message = ""

def new_chat():
    name = _unique_chat_name(f"Chat {len(st.session_state.chats)+1}")
    st.session_state.chats[name] = [
        {"role": "assistant", "content": "Começamos uma novo chat. Como posso ajudar?"}
    ]
    st.session_state.active_chat = name
    bump_chat_to_top(name)

# ----------------------------
# Sidebar (menu fixo + chats / X)
# ----------------------------
with st.sidebar:
    # Menu fixo
    colA, colB = st.columns(2)
    if st.session_state.sidebar_section == "chats":
        st.markdown("### Chats")
        st.button("➕ Novo chat", use_container_width=True, on_click=new_chat)

        st.markdown("---")
        for chat_name in st.session_state.chat_order:
            is_active = (chat_name == st.session_state.active_chat)
            label = f"{chat_name}" if is_active else chat_name

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
# Input (form)
# ----------------------------
with st.form("chat_form", clear_on_submit=True):
    user_text = st.text_area("Mensagem", placeholder="Digite sua mensagem...", label_visibility="collapsed", height=70)
    col1, col2 = st.columns([6, 1])
    with col2:
        send = st.form_submit_button("Enviar")

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

    active_before = st.session_state.active_chat
    st.session_state.chats[active_before].append({"role": "user", "content": injected})

    active_after = maybe_autoname_chat(active_before, injected)
    st.session_state.chats[active_after].append({"role": "assistant", "content": fake_assistant_reply(injected)})

    bump_chat_to_top(active_after)
    st.rerun()

# 2) Envio normal pelo input
if send and user_text.strip():
    txt = user_text.strip()
    active_before = st.session_state.active_chat

    st.session_state.chats[active_before].append({"role": "user", "content": txt})

    active_after = maybe_autoname_chat(active_before, txt)
    st.session_state.chats[active_after].append({"role": "assistant", "content": fake_assistant_reply(txt)})

    bump_chat_to_top(active_after)
    st.rerun()
