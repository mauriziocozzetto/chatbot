import streamlit as st
from groq import Groq

# --- COSTANTI E CONOSCENZA ---
MODELS_INFO = {
    "llama-3.3-70b-versatile": "Il modello più equilibrato e potente, ideale per ragionamenti complessi e conversazioni lunghe.",
    "llama-3.1-8b-instant": "Estremamente veloce e leggero. Perfetto per compiti semplici o risposte immediate.",
    "openai/gpt-oss-120b": "Modello ad alta capacità (se disponibile), ottimizzato per scrittura creativa e analisi approfondite.",
    "openai/gpt-oss-20b": "Versione più rapida della linea GPT-OSS, bilancia bene prestazioni e velocità."
}
MODELS = list(MODELS_INFO.keys())


# --- CONFIGURAZIONE E SETUP ---
def init_page():
    st.set_page_config(page_title="Groq Multi-Model", page_icon="⚡")
    st.title("⚡ Groq Expert Chat")

    with st.sidebar:
        st.header("Configurazione")
        selected_model = st.selectbox(
            "Seleziona il modello AI:",
            options=MODELS,
            key="selected_model"
        )
        st.info(f"**Info modello:** {MODELS_INFO[selected_model]}")
        st.divider()

        if st.button("Pulisci Cronologia"):
            # FIX #2: reset completo che ripristina anche system prompt e benvenuto
            reset_session()
            st.rerun()

    return selected_model


# --- GESTIONE STATO ---
def get_system_prompt(model_name: str) -> dict:
    """Genera il system prompt dinamico con il modello attualmente attivo."""
    info_text = "\n".join([f"- {m}: {desc}" for m, desc in MODELS_INFO.items()])
    return {
        "role": "system",
        "content": (
            f"Sei un assistente esperto. Il modello attualmente in uso è: **{model_name}**.\n"
            f"Conosci i seguenti modelli disponibili in questa app:\n{info_text}\n"
            "Se l'utente te lo chiede, spiega i vantaggi del modello che sta usando rispetto agli altri."
        )
    }


def reset_session(model_name: str = MODELS[0]):
    """Inizializza o resetta la sessione in modo pulito."""
    st.session_state.messages = [
        get_system_prompt(model_name),
        {"role": "assistant", "content": "Ciao! Sono pronto. Chiedimi pure le differenze tra i modelli disponibili!"}
    ]
    st.session_state.last_model = model_name


def init_session_state(model_name: str):
    """Inizializza la sessione e aggiorna il system prompt se il modello cambia."""
    if "messages" not in st.session_state:
        reset_session(model_name)
        return

    # FIX #1: aggiorna il system prompt se l'utente ha cambiato modello
    if st.session_state.get("last_model") != model_name:
        st.session_state.messages[0] = get_system_prompt(model_name)
        st.session_state.last_model = model_name
        st.session_state.messages.append({
            "role": "assistant",
            # FIX #4: notifica visiva del cambio modello
            "content": f"🔄 Modello cambiato in **{model_name}**. {MODELS_INFO[model_name]}"
        })


# --- UI CHAT ---
def display_chat():
    """Visualizza solo i messaggi user e assistant (nasconde il system)."""
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            st.chat_message(msg["role"]).write(msg["content"])


# --- LOGICA DI RISPOSTA ---
def handle_assistant_response(client: Groq, model_name: str):
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        try:
            stream = client.chat.completions.create(
                model=model_name,
                messages=st.session_state.messages,
                stream=True,
            )

            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_response += delta
                    placeholder.markdown(full_response + "▌")

            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Errore API: {e}")


# --- MAIN ---
def main():
    selected_model = init_page()

    # FIX #3: client inizializzato una sola volta per sessione
    if "client" not in st.session_state:
        st.session_state.client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    init_session_state(selected_model)
    display_chat()

    if prompt := st.chat_input("Chiedimi delle differenze tra i modelli..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        handle_assistant_response(st.session_state.client, selected_model)


if __name__ == "__main__":
    main()
