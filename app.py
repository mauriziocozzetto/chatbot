import streamlit as st
from groq import Groq

groq_api_key = st.secrets.get("GROQ_API_KEY")

st.title("💬 Groq Chatbot")

# Inizializzazione della cronologia dei messaggi
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content":
            "Ciao! Sono un assistente potenziato da Groq. Come posso aiutarti?"}]

# Visualizzazione dei messaggi precedenti
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Input dell'utente
if prompt := st.chat_input():
    if not groq_api_key:
        st.info("Per favore, aggiungi la tua API key di Groq per continuare.")
        st.stop()

    # Inizializzazione del client Groq
    client = Groq(api_key=groq_api_key)

    # Aggiunta del messaggio utente alla sessione e visualizzazione
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Chiamata API a Groq
    # Nota: il modello aggiornato è 'llama-3.3-70b-versatile'
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
        )

        msg = response.choices[0].message.content

        # Aggiunta della risposta dell'assistente alla sessione e visualizzazione
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)

    except Exception as e:
        st.error(f"Si è verificato un errore: {e}")
