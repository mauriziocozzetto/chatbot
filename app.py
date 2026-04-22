import streamlit as st
from groq_client import GroqChatClient
from chat_manager import ChatHistoryManager
import time

st.set_page_config(page_title="Groq AI Chat", layout="wide", page_icon="🤖")

def main():
    client = GroqChatClient()
    chat = ChatHistoryManager()

    if not client.is_configured():
        st.error("Errore: GROQ_API_KEY non trovata in .streamlit/secrets.toml")
        st.stop()

    # --- SIDEBAR CONFIGURAZIONE ---
    with st.sidebar:
        st.header("Configurazione")
        model_id = st.selectbox("Modello AI:", client.get_available_models(), key="model_selector")
        
        if st.button("Mostra Info Modello"):
            st.info(client.get_model_capabilities(model_id))
        
        st.divider()
        temp = st.slider("Temperatura (Creatività):", 0.0, 2.0, 0.2, step=0.1)
        max_user_msg = st.slider("Limite Messaggi Utente:", 5, 50, 20)
        
        st.divider()
        if st.button("Pulisci Cronologia"):
            chat.clear_history()
            st.rerun()

    # Sincronizziamo l'identità del modello selezionato prima di ogni interazione
    chat.sync_system_prompt(model_id)

    # --- VISUALIZZAZIONE CHAT ---
    for msg in chat.get_messages():
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # --- INFO BAR (CONTATORE + MODELLO) ---
    # Posizionata appena sopra l'input per massima visibilità
    current_user_count = chat.count_user_messages()
    
    # Creiamo una riga formattata con emoji per distinguere le info
    st.markdown(
        f"**Modello attivo:** `{model_id}` |  **Messaggi inviati:** `{current_user_count} / {max_user_msg}`"
    )
    
    # --- GESTIONE INPUT ---
    if prompt := st.chat_input("Chiedimi delle differenze tra i modelli..."):
        
        # 1. Aggiunta messaggio utente
        chat.add_message("user", prompt)
        st.chat_message("user").markdown(prompt)

        # 2. Risposta in streaming
        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""
            stream = client.stream_chat_response(chat.get_messages(), model_id, temp)
            
            if stream:
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        placeholder.markdown(full_response + "▌")
                
                placeholder.markdown(full_response)
                chat.add_message("assistant", full_response)

        # 3. Controllo reset e aggiornamento interfaccia
        if chat.check_and_reset_if_limit_reached(max_user_msg):
            st.warning(f"⚠️ Limite di {max_user_msg} messaggi raggiunto. Reset della conversazione in corso...")
            time.sleep(2)
            st.rerun()
        else:
            # Forza il refresh per aggiornare il contatore numerico in tempo reale
            st.rerun()

if __name__ == "__main__":
    main()  
