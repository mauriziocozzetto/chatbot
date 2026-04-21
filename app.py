import streamlit as st
from groq import Groq

# --- CONFIGURAZIONE E COSTANTI ---
MODEL_NAME = "llama-3.3-70b-versatile"

def init_page():
    """Configura l'aspetto della pagina e il titolo."""
    st.set_page_config(page_title="Groq Professional Chat", page_icon="⚡")
    st.title("⚡ Groq API Streamliner")

def get_client():
    """Inizializza il client Groq prelevando la chiave dai secrets."""
    try:
        return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except KeyError:
        st.error("Configura 'GROQ_API_KEY' nei Secrets di Streamlit!")
        st.stop()

# --- GESTIONE DATI ---
def init_session_state():
    """Inizializza la cronologia se vuota."""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Ciao! Come posso aiutarti oggi?"}
        ]

def add_message(role, content):
    """Aggiunge un messaggio alla sessione e lo visualizza."""
    st.session_state.messages.append({"role": role, "content": content})
    st.chat_message(role).write(content)

# --- LOGICA DI CHAT ---
def generate_response(client):
    """Gestisce la chiamata API e lo streaming della risposta."""
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        try:
            stream = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": m["role"], "content": m["content"]} 
                          for m in st.session_state.messages],
                stream=True,
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Errore API: {e}")

# --- MAIN LOOP ---
def main():
    init_page()
    init_session_state()
    client = get_client()

    # Visualizza lo storico esistente
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Gestione nuovo input
    if prompt := st.chat_input("Chiedimi qualcosa..."):
        # Usiamo la routine per aggiungere il messaggio dell'utente
        add_message("user", prompt)
        # Generiamo la risposta dell'assistente
        generate_response(client)

if __name__ == "__main__":
    main()
