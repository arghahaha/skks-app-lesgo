import os
from openai import OpenAI
from dotenv import load_dotenv
import logging
import time
import pandas as pd
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ai-analyzer')

# Load environment variables from .env file
load_dotenv()

# Configure OpenAI
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it in your .env file.")

logger.info(f"API Key loaded: {api_key[:8]}...")

def get_llm_response(prompt):
    """
    Get response from LLM for interpretation generation
    
    Args:
        prompt: String containing the prompt for LLM
        
    Returns:
        String containing the LLM response
    """
    try:
        response = OpenAI(api_key=api_key).chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Anda adalah asisten yang ahli dalam menganalisis hasil penilaian kesadaran keamanan siber. Berikan interpretasi yang komprehensif, profesional, dan mudah dipahami."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error getting LLM response: {str(e)}")
        raise

def analyze_responses(personal_data, responses):
    """
    Analyze questionnaire responses using LLM
    
    Args:
        personal_data: Dictionary containing personal information
        responses: Dictionary containing questionnaire responses
        
    Returns:
        String containing the analysis and recommendations
    """
    try:
        # Prepare data for LLM
        analysis_data = {
            'personal_data': personal_data,
            'responses': responses
        }
        
        # Create prompt for LLM
        prompt = f"""Berdasarkan data berikut, berikan analisis dan rekomendasi untuk meningkatkan kesadaran keamanan siber:

Data Pribadi:
- Nama: {personal_data['name']}
- Pendidikan: {personal_data['education']}
- Domisili: {personal_data['domicile']}

Jawaban Kuesioner:
{json.dumps(responses, indent=2)}

Berdasarkan data di atas, berikan:
1. Analisis kesadaran keamanan siber secara keseluruhan
2. Rekomendasi spesifik untuk meningkatkan kesadaran keamanan siber
3. Langkah-langkah praktis yang dapat diterapkan dalam kehidupan sehari-hari

Format rekomendasi:
- Gunakan bahasa yang profesional namun mudah dipahami
- Berikan contoh konkret untuk setiap rekomendasi
- Fokus pada aspek praktis yang dapat diterapkan
- Sesuaikan rekomendasi dengan tingkat pendidikan dan konteks domisili
"""

        # Get analysis from LLM
        analysis = get_llm_response(prompt)
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing responses: {str(e)}")
        return "Terjadi kesalahan dalam menganalisis jawaban. Silakan coba lagi nanti."

def analyze_responses_old(personal_data, responses):
    """
    Analyze questionnaire responses using OpenAI API
    
    Args:
        personal_data: Dictionary containing personal information
        responses: Dictionary containing questionnaire responses
        
    Returns:
        String containing personalized recommendations
    """
    # Initialize client with API key
    client = OpenAI(api_key=api_key)
    
    # Format responses for better LLM understanding
    formatted_responses = []
    likert_scale = {
        "1": "Sangat Tidak Setuju",
        "2": "Tidak Setuju",
        "3": "Setuju",
        "4": "Sangat Setuju"
    }
    
    # Load questions for context
    try:
        df_questions = pd.read_excel('data/question.xlsx')
        questions_dict = {f"q{row['id']}": row['question'] for _, row in df_questions.iterrows()}
        
        # Format each response with its question
        for q_id, answer in responses.items():
            if q_id.startswith('q'):  # Only process question responses
                question_text = questions_dict.get(q_id, "Pertanyaan tidak ditemukan")
                answer_text = likert_scale.get(answer, "Jawaban tidak valid")
                formatted_responses.append(f"Pertanyaan: {question_text}\nJawaban: {answer_text}\n")
    except Exception as e:
        logger.error(f"Error formatting responses: {str(e)}")
        # Fallback to raw responses if formatting fails
        formatted_responses = [f"{k}: {v}" for k, v in responses.items()]
    
    # Prepare the context-based prompt without personal identifiers
    context_prompt = f"""
    Sebagai pakar keamanan siber, analisis respons kuesioner berikut:
    
    Respons Kuesioner:
    {''.join(formatted_responses)}
    
    Tugas Anda:
    Berikan satu rekomendasi praktis dan edukatif untuk masing-masing kategori tingkat kesadaran keamanan siber:
    • Sangat rendah
    • Rendah
    • Sedang
    • Tinggi

    Setiap rekomendasi harus:
    • Praktis dan dapat langsung diterapkan
    • Mengedukasi dengan menjelaskan alasan pentingnya
    • Disampaikan secara formal dan instruktif

    Format hasil:
    1. Tingkat Kesadaran Sangat Rendah
       • Rekomendasi: [Rekomendasi spesifik]
       • Alasan: [Penjelasan pentingnya]
       • Langkah Implementasi: [Langkah-langkah praktis]

    2. Tingkat Kesadaran Rendah
       • Rekomendasi: [Rekomendasi spesifik]
       • Alasan: [Penjelasan pentingnya]
       • Langkah Implementasi: [Langkah-langkah praktis]

    3. Tingkat Kesadaran Sedang
       • Rekomendasi: [Rekomendasi spesifik]
       • Alasan: [Penjelasan pentingnya]
       • Langkah Implementasi: [Langkah-langkah praktis]

    4. Tingkat Kesadaran Tinggi
       • Rekomendasi: [Rekomendasi spesifik]
       • Alasan: [Penjelasan pentingnya]
       • Langkah Implementasi: [Langkah-langkah praktis]

    Catatan Penting:
    - Jangan tampilkan skor dalam hasil
    - Format hasil dalam poin-poin
    - Berikan contoh konkret yang dapat langsung diterapkan
    - Fokus pada area yang mendapat skor rendah dalam kuesioner
    """
    
    # Set maximum retries
    max_retries = 3
    retries = 0
    backoff_factor = 1
    
    while retries < max_retries:
        try:
            logger.info(f"Calling OpenAI API (attempt {retries + 1}/{max_retries})...")
            start_time = time.time()
            
            # Make API call with timeout
            response = client.chat.completions.create(
                model="GPT-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Anda adalah pakar keamanan siber yang memberikan rekomendasi praktis dan edukatif berdasarkan tingkat kesadaran keamanan siber responden. Berikan rekomendasi yang dapat langsung diterapkan dan disertai penjelasan pentingnya."},
                    {"role": "user", "content": context_prompt}
                ],
                temperature=0.7,
                max_tokens=1000,  # Increased token limit for more detailed recommendations
                timeout=30  # 30 seconds timeout
            )
            
            elapsed = time.time() - start_time
            logger.info(f"OpenAI API call completed in {elapsed:.2f} seconds")
            
            return response.choices[0].message.content
            
        except Exception as e:
            retries += 1
            logger.error(f"Error in OpenAI API call (attempt {retries}/{max_retries}): {str(e)}")
            
            if retries >= max_retries:
                logger.error("Maximum retries reached, returning fallback message")
                return "Mohon maaf, kami tidak dapat menghasilkan rekomendasi saat ini. Silakan coba lagi nanti."
            
            # Exponential backoff
            sleep_time = backoff_factor * (2 ** (retries - 1))
            logger.info(f"Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time) 