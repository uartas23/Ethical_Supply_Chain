import streamlit as st
import google.generativeai as genai

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="SourceRight", page_icon="🌍", layout="centered")

st.title("🌍 SourceRight")
st.markdown("Your GenAI assistant for designing responsible vendor policies.")

# --- API KEY AUTHENTICATION ---
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter your Gemini API Key:", type="password")
    st.markdown("---")
    st.markdown("**How it works:**\nThis app uses Generative AI to guide you through a 5-step process to build ethical compliance clauses and audit frameworks for your vendors.")

# --- SYSTEM INSTRUCTIONS (THE AI PERSONA) ---
SYSTEM_PROMPT = """
You are the SourceRight, an expert AI consultant in ESG, human rights, and sustainable procurement.
Your goal is to guide the user step-by-step to create an ethical Code of Conduct and Audit Checklist for their vendors.

You MUST follow this exact 5-step process. Do NOT jump ahead. Ask one question at a time and wait for the user's response.

Step 1: Identify Sourcing Category (Ask what raw material or service they are procuring).
Step 2: Systemic Risk Mapping (Explain common ESG risks in that specific industry and ask which ones to prioritize).
Step 3: Define Vendor Requirements (Ask if they want third-party certification or custom internal compliance clauses).
Step 4: GenAI Drafting (Generate the formal compliance clause based on their choices and ask if it fits their corporate tone).
Step 5: Audit Checklist (Generate 5 actionable, specific audit questions to evaluate the vendor against the drafted clause).

Keep your tone professional, consultative, and encouraging. Focus heavily on 'Responsible Business' principles.
"""

# --- MAIN APP LOGIC ---
if api_key:
    # 1. Konfigurasi API
    genai.configure(api_key=api_key)
    
    # 2. AUTO-DETECT MODEL: Mencari nama model yang valid dan didukung API Key kamu
    try:
        available_models = [m.name for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
        
        # Prioritaskan mencari model 1.5 flash yang ringan
        target_model = None
        for m in available_models:
            if "1.5-flash" in m:
                target_model = m
                break
                
        # Jika tidak ada, ambil model apapun yang mengandung kata "flash" atau "pro"
        if not target_model:
            for m in available_models:
                if "flash" in m or "pro" in m:
                    target_model = m
                    break
        
        # 3. Jalankan Aplikasi jika model ditemukan
        if target_model:
            model = genai.GenerativeModel(
                model_name=target_model,
                system_instruction=SYSTEM_PROMPT
            )
            
            if "chat_session" not in st.session_state:
                st.session_state.chat_session = model.start_chat(history=[])
                
                initial_greeting = f"Hello! I am your Ethical Supply Chain Co-Pilot (Running on `{target_model}`). To get started with our 5-step process, what raw material or service are you currently procuring? (e.g., Factory Uniforms)"
                st.session_state.messages = [{"role": "assistant", "content": initial_greeting}]

            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            if prompt := st.chat_input("Type your response here..."):
                st.chat_message("user").markdown(prompt)
                st.session_state.messages.append({"role": "user", "content": prompt})

                with st.chat_message("assistant"):
                    with st.spinner("Analyzing..."):
                        response = st.session_state.chat_session.send_message(prompt)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
        else:
            st.error("Gagal menemukan model yang kompatibel. Pastikan API Key valid.")
            
    except Exception as e:
        st.error(f"Terjadi kesalahan saat menghubungi Google API: {e}")
        
else:
    st.info("👈 Please enter your Gemini API Key in the sidebar to start.")
