import os
from openai import OpenAI
from dotenv import load_dotenv
import logging
import time
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ai-analyzer')

load_dotenv()

# Configure OpenAI
api_key = os.getenv('OPENAI_API_KEY')
logger.info(f"API Key loaded: {api_key[:8] if api_key and len(api_key) >= 8 else 'Not Found'}...")

def analyze_responses(personal_data, responses):
    """
    Analyze questionnaire responses using OpenAI API
    
    Args:
        personal_data: Dictionary containing personal information
        responses: Dictionary containing questionnaire responses
        
    Returns:
        String containing personalized recommendations
    """
    # Initialize client with minimal configuration
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
    Sebagai ahli keamanan siber, analisis data dan respons kuesioner responden berikut:
    
    Profil Responden:
    - Pendidikan: {personal_data['education']}
    - Lokasi: {personal_data['domicile']}
    - Jenis Kelamin: {personal_data['gender']}
    
    Respons Kuesioner:
    {''.join(formatted_responses)}
    
    Tugas Anda:
    1. Analisis setiap jawaban kuesioner dengan cermat
    2. Identifikasi area yang perlu ditingkatkan berdasarkan jawaban "Tidak Setuju" dan "Sangat Tidak Setuju"
    3. Berikan rekomendasi yang spesifik dan sesuai dengan:
       - Tingkat pendidikan responden
       - Jawaban spesifik yang diberikan
       - Konteks lokasi responden
    
    Format rekomendasi:

    1. TINDAKAN PENTING (Berdasarkan Jawaban Lemah)
       - Fokus pada 2-3 area yang mendapat jawaban "Tidak Setuju" atau "Sangat Tidak Setuju"
       - Berikan langkah konkret untuk meningkatkan area tersebut
       - Contoh: Jika responden tidak menggunakan kata sandi yang berbeda, berikan panduan membuat dan mengelola kata sandi yang aman

    2. PENGUATAN KEAMANAN (Berdasarkan Profil)
       - Berikan 3-4 praktik keamanan yang sesuai dengan tingkat pendidikan
       - Sesuaikan kompleksitas rekomendasi dengan latar belakang responden
       - Contoh: Untuk responden dengan pendidikan dasar, fokus pada praktik keamanan dasar yang mudah dipahami

    3. PELATIHAN & PENGEMBANGAN
       - Rekomendasikan sumber belajar yang sesuai dengan:
         * Tingkat pendidikan responden
         * Area yang perlu ditingkatkan
         * Ketersediaan sumber di lokasi responden
       - Berikan link atau nama platform yang dapat diakses

    4. ALAT & SUMBER DAYA
       - Rekomendasikan alat yang:
         * Mudah digunakan sesuai tingkat pendidikan
         * Gratis atau terjangkau
         * Tersedia di lokasi responden
       - Berikan panduan langkah demi langkah penggunaan

    Catatan Penting:
    - Setiap rekomendasi HARUS terkait langsung dengan jawaban kuesioner
    - Hindari rekomendasi umum yang tidak relevan dengan jawaban
    - Sesuaikan bahasa dan kompleksitas dengan tingkat pendidikan
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
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Anda adalah ahli keamanan siber yang memberikan rekomendasi yang sangat spesifik dan sesuai dengan jawaban kuesioner responden. Fokus pada area yang mendapat skor rendah dan berikan solusi praktis yang sesuai dengan latar belakang responden."},
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