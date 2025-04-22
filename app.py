from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import re

app = Flask(__name__)

# Configure your Gemini API key
GEMINI_API_KEY = "AIzaSyCIcGz1PhgZ7bxOcBtsQaaSTLlDFEauPuQ"
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-1.5-flash-8b')

# Healthcare-related keywords
healthcare_keywords = [
    "health", "wellness", "fitness", "diet", "nutrition", "hygiene", "sanitation", "stress", "sleep", "fatigue", "hydration",
    "headache", "fever", "cough", "cold", "sore throat", "nausea", "vomiting", "dizziness", "chest pain", "stomach ache",
    "joint pain", "muscle pain", "diarrhea", "constipation", "rash", "swelling", "itching", "bleeding", "infection",
    "flu", "covid", "diabetes", "hypertension", "asthma", "cancer", "heart disease", "arthritis", "migraine",
    "depression", "anxiety", "obesity", "malaria", "tuberculosis", "anemia", "stroke", "ulcer", "epilepsy",
    "medicine", "tablet", "pill", "injection", "vaccine", "antibiotics", "painkiller", "therapy", "surgery", "treatment",
    "prescription", "dose", "ointment", "syrup", "insulin", "chemotherapy", "radiation", "IV", "inhaler",
    "diagnosis", "test", "scan", "x-ray", "MRI", "CT scan", "blood test", "urine test", "biopsy", "ECG", "checkup", "screening",
    "doctor", "nurse", "surgeon", "physician", "dentist", "therapist", "specialist", "pediatrician", "dermatologist",
    "psychiatrist", "gynecologist", "oncologist", "cardiologist", "neurologist", "general practitioner", "paramedic", "pharmacist",
    "hospital", "clinic", "pharmacy", "emergency", "ICU", "OPD", "ward", "ambulance", "healthcare center", "lab", "nursing home",
    "cardiology", "neurology", "dermatology", "pediatrics", "psychiatry", "gynecology", "oncology", "orthopedics", 
    "endocrinology", "urology", "nephrology", "gastroenterology", "immunology",
    "mental health", "therapy", "counseling", "psychologist", "trauma", "PTSD", "mood disorder", "bipolar",
    "pregnancy", "childbirth", "labor", "breastfeeding", "menstruation", "cramps", "fertility", "menopause", "ovulation", "prenatal", "postpartum",
    "pediatric", "vaccination", "quarantine", "epidemic", "pandemic", "mask", "social distancing", "prevention", "awareness", "piles", "erectile disfunction"
]

# Phrases to remove from model response
phrases_to_remove = [
    "I can't offer medical advice, but here are some things you might try:",
    "I'm not a doctor, but",
    "Consult a medical professional if you're unsure.",
    "It's best to speak with a healthcare provider.",
    "This is not a substitute for professional medical advice.",
    "I'm a language model and cannot give medical advice."
]

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/ask', methods=['POST'])
def ask():
    user_query = request.form['query'].lower()

    if any(keyword in user_query for keyword in healthcare_keywords):
        stylized_prompt = (
            "You are a professional healthcare assistant. When the user asks a health-related question, always respond in the following strict format:\n\n"
            "Possible Cause(s):\n"
            "- ...\n"
            "- ...\n\n"
            "Suggested Medicines (OTC):\n"
            "- ...\n"
            "- ...\n\n"
            "Home Remedies:\n"
            "- ...\n"
            "- ...\n"
            "- ...\n"
            "- ...\n\n"
            "Respond clearly, concisely, and include all 3 sections even if speculative. Do not add any extra disclaimers or irrelevant information.\n\n"
            f"User: {user_query}"
        )

        response = model.generate_content(stylized_prompt)
        response_text = response.text.strip()

        # Remove unwanted phrases
        for phrase in phrases_to_remove:
            response_text = response_text.replace(phrase, '')

        # Extract sections using regex
        def extract_section(header_title, full_text):
            pattern = rf"{header_title}[:\-]?\s*\n((?:- .+\n?)+)"
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                return [line.strip('- ').strip() for line in match.group(1).split('\n') if line.strip()]
            return []


        causes = extract_section("Possible Cause\\(s\\)", response_text)
        medicines = extract_section("Suggested Medicines \\(OTC\\)", response_text)
        remedies = extract_section("Home Remedies", response_text)


        return jsonify({
            "causes": causes,
            "medicines": medicines,
            "remedies": remedies
        })
    else:
        return jsonify({'causes': [], 'medicines': [], 'remedies': []})

if __name__ == '__main__':
    app.run(debug=True)
