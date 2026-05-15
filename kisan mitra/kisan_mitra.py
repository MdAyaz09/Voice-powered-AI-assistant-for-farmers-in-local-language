import streamlit as st
import datetime
import random
import time
from fpdf import FPDF
import base64
import matplotlib.pyplot as plt
from langdetect import detect
import speech_recognition as sr

# Set matplotlib backend
plt.switch_backend('Agg')

# ====================== APP CONFIGURATION ======================
st.set_page_config(
    page_title="Kisan Mitra - AI Farming Assistant",
    page_icon="🌾",
    layout="centered"
)

# Custom CSS styling
st.markdown("""
<style>
    .stTextInput>div>div>input {
        background-color: #f0f8ff;
        border: 1px solid #4CAF50;
    }
    .assistant-response {
        background-color: #e6f7e6;
        padding: 12px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #4CAF50;
    }
    .language-radio .stRadio > div {
        flex-direction: row !important;
        gap: 15px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
    }
    .submit-btn {
        margin-top: 10px;
        width: 100%;
    }
    [data-testid="stSidebar"] {
        background: #f0fff0;
    }
</style>
""", unsafe_allow_html=True)

# ====================== LANGUAGE SETUP ======================
LANGUAGES = {
    "हिंदी": "hi",
    "English": "en", 
    "తెలుగు": "te"
}

# Initialize session state
if 'lang' not in st.session_state:
    st.session_state.lang = "English"
if 'submit_clicked' not in st.session_state:
    st.session_state.submit_clicked = False
if 'voice_transcript' not in st.session_state:
    st.session_state.voice_transcript = ""

# ====================== MULTILINGUAL CONTENT ======================
CONTENT = {
    "title": {
        "हिंदी": "किसान मित्र - AI कृषि सहायक",
        "English": "Kisan Mitra - AI Farming Assistant", 
        "తెలుగు": "కిసాన్ మిత్ర్ - AI వ్యవసాయ సహాయకుడు"
    },
    "welcome": {
        "हिंदी": "किसान मित्र में आपका स्वागत है!",
        "English": "Welcome to Kisan Mitra!",
        "తెలుగు": "కిసాన్ మిత్ర్ కు స్వాగతం!"
    },
    "prompt": {
        "हिंदी": "अपना कृषि प्रश्न टाइप करें:",
        "English": "Type your farming question:",
        "తెలుగు": "మీ వ్యవసాయ ప్రశ్నను టైప్ చేయండి:"
    },
    "submit": {
        "हिंदी": "प्रश्न पूछें",
        "English": "Ask Question",
        "తెలుగు": "ప్రశ్న అడగండి"
    },
    "responses": {
        "weather": {
            "हिंदी": "आज का मौसम: {}°C, {}. आर्द्रता: {}%",
            "English": "Today's weather: {}°C, {}. Humidity: {}%",
            "తెలుగు": "నేటి వాతావరణం: {}°C, {}. ఆర్ద్రత: {}%"
        },
        "fertilizer": {
            "हिंदी": "{} के लिए: रोपण के समय NPK 10-10-10 का उपयोग करें, फलने के दौरान उच्च पोटेशियम उर्वरक पर स्विच करें",
            "English": "For {}: Use NPK 10-10-10 during planting, switch to high-potassium fertilizer during fruiting",
            "తెలుగు": "{} కోసం: నాటడం సమయంలో NPK 10-10-10 ఉపయోగించండి, పండ్ల సమయంలో అధిక పొటాషియం ఎరువుకు మారండి"
        },
        "price": {
            "हिंदी": "{} का वर्तमान बाजार भाव: ₹{} प्रति क्विंटल",
            "English": "Current market price for {}: ₹{} per quintal",
            "తెలుగు": "{} యొక్క ప్రస్తుత మార్కెట్ ధర: ₹{} ప్రతి క్వింటాల్కు"
        }
    }
}

# ====================== KNOWLEDGE BASE ======================
def get_weather(lang):
    """Generate localized weather forecast"""
    temp = random.randint(25, 38)
    conditions = {
        "हिंदी": ["धूप", "आंशिक बादल", "बरसात"],
        "English": ["Sunny", "Partly Cloudy", "Rainy"],
        "తెలుగు": ["ఎండ", "మేఘావృతం", "వర్షం"]
    }
    condition = random.choice(conditions[lang])
    humidity = random.randint(60, 85)
    return CONTENT["responses"]["weather"][lang].format(temp, condition, humidity)

def get_fertilizer_advice(crop, lang):
    """Provide crop-specific fertilizer advice"""
    crops = {
        "tomato": {
            "हिंदी": "टमाटर",
            "English": "tomato",
            "తెలుగు": "టమాట"
        },
        "paddy": {
            "हिंदी": "धान",
            "English": "paddy",
            "తెలుగు": "వరి"
        }
    }
    crop_name = crops.get(crop, {}).get(lang, crop)
    return CONTENT["responses"]["fertilizer"][lang].format(crop_name)

def get_price(crop, lang):
    """Get localized market prices"""
    prices = {
        "tomato": random.randint(1800, 2500),
        "onion": random.randint(1500, 2200),
        "rice": random.randint(3500, 4800),
        "paddy": random.randint(1200, 1800)
    }
    
    crop_names = {
        "tomato": {
            "हिंदी": "टमाटर",
            "English": "tomato",
            "తెలుగు": "టమాట"
        },
        "onion": {
            "हिंदी": "प्याज",
            "English": "onion",
            "తెలుగు": "ఉల్లి"
        }
    }
    
    for c in prices:
        if c in crop:
            localized_crop = crop_names.get(c, {}).get(lang, c)
            return CONTENT["responses"]["price"][lang].format(localized_crop, prices[c])
    
    return {
        "हिंदी": "मैं टमाटर, प्याज, धान की कीमतें बता सकता हूँ",
        "English": "I can provide prices for tomato, onion, paddy",
        "తెలుగు": "నేను టమాటా, ఉల్లి, వరి ధరలు అందించగలను"
    }[lang]

# ====================== SPEECH RECOGNITION ======================
def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak now.")
        audio = r.listen(source)
        try:
            return r.recognize_google(audio)
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return ""

# ====================== MAIN APP INTERFACE ======================
# Sidebar configuration
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3079/3079151.png", width=100)
    st.markdown("### 🌍 Sustainable Farming Assistant")
    st.markdown("Ask about:")
    st.markdown("- Weather forecasts")
    st.markdown("- Crop prices")
    st.markdown("- Farming advice")
    st.markdown("---")
    st.caption("Built with ❤️ for Indian farmers")

# Language selection
with st.container():
    st.markdown('<div class="language-radio">', unsafe_allow_html=True)
    lang = st.radio(
        "",
        options=["हिंदी", "English", "తెలుగు"],
        index=["हिंदी", "English", "తెలుగు"].index(st.session_state.lang),
        horizontal=True,
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    st.session_state.lang = lang

# Main title
st.title(CONTENT["title"][lang])
st.markdown(f"### {CONTENT['welcome'][lang]}")

# Main content area
# Add input method selection
input_method = st.radio(
    "Input Method" if lang == "English" else "इनपुट विधि" if lang == "हिंदी" else "ఇన్పుట్ పద్ధతి",
    ["Text Input", "Voice Input"],
    key="input_method"
)

# Voice recording section (outside the form)
if input_method == "Voice Input":
    col1, col2 = st.columns([3, 1])
    with col1:
        voice_placeholder = st.empty()
        user_input = voice_placeholder.text_area(
            "Transcribed Text" if lang == "English" else "ट्रांसक्राइब्ड टेक्स्ट" if lang == "हिंदी" else "ట్రాన్స్క్రిబ్డ్ టెక్స్ట్",
            value=st.session_state.voice_transcript,
            height=100
        )
    with col2:
        if st.button("🎙 " + ("Record Voice" if lang == "English" else "आवाज रिकॉर्ड करें" if lang == "हिंदी" else "వాయిస్ రికార్డ్ చేయండి")):
            with st.spinner("Listening..." if lang == "English" else "सुन रहा हूँ..." if lang == "हिंदी" else "వినడం..."):
                transcript = speech_to_text()
                st.session_state.voice_transcript = transcript
                voice_placeholder.text_area(
                    "Transcribed Text" if lang == "English" else "ट्रांसक्राइब्ड टेक्स्ट" if lang == "हिंदी" else "ట్రాన్స్క్రిబ్డ్ టెక్స్ట్",
                    value=transcript,
                    height=100
                )

# Form for submission (works for both text and voice input)
with st.form("question_form"):
    if input_method == "Text Input":
        user_input = st.text_input(
            CONTENT["prompt"][lang],
            key="user_input",
            label_visibility="visible"
        )
    
    submitted = st.form_submit_button(CONTENT["submit"][lang])
    
    if submitted and user_input:
        with st.spinner("Processing..." if lang == "English" else 
                      "प्रसंस्करण..." if lang == "हिंदी" else 
                      "ప్రాసెస్ చేయడం..."):
            time.sleep(1)  # Simulate processing
            
            # Detect input language
            try:
                detected_lang = detect(user_input)
                lang_code = {"hi": "हिंदी", "en": "English", "te": "తెలుగు"}.get(detected_lang[:2], lang)
            except:
                lang_code = lang
            
            # Process query
            query = user_input.lower()
            response = ""
            
            # Weather queries
            weather_words = {
                "हिंदी": ["मौसम", "बारिश", "तापमान"],
                "English": ["weather", "rain", "temperature"],
                "తెలుగు": ["వాతావరణం", "వర్షం", "ఉష్ణోగ్రత"]
            }
            if any(word in query for word in weather_words[lang_code]):
                response = get_weather(lang_code)
            
            # Fertilizer queries
            elif "fertilizer" in query or "उर्वरक" in query or "ఎరువు" in query:
                crop = "tomato" if "tomato" in query or "टमाटर" in query or "టమాట" in query else "paddy"
                response = get_fertilizer_advice(crop, lang_code)
            
            # Price queries
            elif "price" in query or "भाव" in query or "ధర" in query:
                crop = "tomato" if "tomato" in query or "टमाटर" in query or "టమాట" in query else "onion"
                response = get_price(crop, lang_code)
            
            else:
                response = {
                    "हिंदी": f"आपने पूछा: '{user_input}'\n\nमैं मौसम, उर्वरक सलाह और फसल की कीमतों के बारे में जानकारी दे सकता हूँ",
                    "English": f"You asked: '{user_input}'\n\nI can provide weather, fertilizer advice and crop prices",
                    "తెలుగు": f"మీరు అడిగారు: '{user_input}'\n\nనేను వాతావరణం, ఎరువు సలహాలు మరియు పంట ధరలను అందించగలను"
                }[lang_code]
            
            # Display response
            st.markdown(f'<div class="assistant-response">🤖 {response}</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
footer_text = {
    "हिंदी": "किसानों के लिए AI सहायक • हिंदी/अंग्रेजी/तेलुगु समर्थित • 🌱 सतत कृषि",
    "English": "AI Assistant for Farmers • Hindi/English/Telugu Supported • 🌱 Sustainable Agriculture",
    "తెలుగు": "రైతుల కోసం AI సహాయకుడు • హిందీ/ఆంగ్ల/తెలుగు మద్దతు • 🌱 స్థిరమైన వ్యవసాయం"
}
st.caption(footer_text.get(lang, "Built for Farmers"))
#pip install streamlit
#python -m streamlit run kisan_mitra.py
