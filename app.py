from flask import Flask, render_template, request, send_file, jsonify, session
import pandas as pd
from datetime import datetime
import os
import logging
from dotenv import load_dotenv
from utils.certificate_generator import generate_certificate
from utils.ai_analyzer import analyze_responses
import traceback
from utils.assessment_evaluator import evaluate_responses

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('skks-app')

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set secret key for session management

# Ensure required directories exist
os.makedirs('data', exist_ok=True)
os.makedirs('certificates', exist_ok=True)

# Load questions from Excel file
def load_questions():
    try:
        logger.info("Loading questions from Excel file...")
        
        # Check if file exists
        question_file = 'data/question.xlsx'
        
        if not os.path.exists(question_file):
            logger.error(f"Question file not found: {question_file}")
            raise FileNotFoundError(f"Question file not found: {question_file}")
        
        # Load questions
        logger.info("Reading questions from Excel...")
        df_questions = pd.read_excel(question_file)
        logger.info(f"Found {len(df_questions)} questions in Excel")
        
        questions = []
        for _, row in df_questions.iterrows():
            # Handle potential missing values
            question_text = str(row['question']).strip() if pd.notna(row['question']) else ""
            category = str(row['category']).strip() if pd.notna(row['category']) else "Umum"
            
            if question_text:  # Only add non-empty questions
                questions.append({
                    'id': f"q{row['id']}",
                    'text': question_text,
                    'category': category
                })
        
        if not questions:
            logger.error("No valid questions found in the Excel file")
            raise ValueError("No valid questions found in the Excel file")
            
        # Define Likert scale options (4-point scale)
        likert_scale = [
            "Sangat Tidak Setuju",
            "Tidak Setuju",
            "Setuju",
            "Sangat Setuju"
        ]
            
        logger.info(f"Successfully loaded {len(questions)} questions")
        return {
            'questions': questions,
            'likert_scale': likert_scale
        }
    except FileNotFoundError as e:
        logger.error(f"File not found error: {str(e)}")
        return None
    except pd.errors.EmptyDataError:
        logger.error("Excel file is empty")
        return None
    except Exception as e:
        logger.error(f"Error loading questions: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None

# Load questions at startup
QUESTIONS = load_questions()
if QUESTIONS is None:
    logger.error("Failed to load questions at startup")
    print("⚠️ Warning: Failed to load questions. Please check the log file for details.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/personal_data')
def personal_data():
    return render_template('personal_data.html')

@app.route('/questionnaire')
def questionnaire():
    if QUESTIONS is None:
        return "Error loading questions. Please try again later.", 500
    return render_template('questionnaire.html', 
                         questions=QUESTIONS['questions'],
                         likert_scale=QUESTIONS['likert_scale'])

@app.route('/submit_personal_data', methods=['POST'])
def submit_personal_data():
    try:
        data = request.form
        session['personal_data'] = {
            'name': data['name'],
            'age': data['age'],
            'education': data['education'],
            'domicile': data['domicile'],
            'gender': data['gender']
        }
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error in submit_personal_data: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/submit_questionnaire', methods=['POST'])
def submit_questionnaire():
    try:
        logger.info("Starting questionnaire submission...")
        responses = request.form
        logger.info(f"Received responses: {responses}")
        
        personal_data = session.get('personal_data')
        logger.info(f"Retrieved personal data: {personal_data}")
        
        if not personal_data:
            logger.warning("No personal data found in session")
            return jsonify({'status': 'error', 'message': 'Personal data not found'}), 400
        
        # Prepare data for Excel storage
        data_to_store = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            **personal_data,
            **responses
        }
        logger.info("Prepared data for Excel storage")
        
        # Store in Excel
        excel_path = 'data/responses.xlsx'
        new_df = pd.DataFrame([data_to_store])
        
        try:
            if os.path.exists(excel_path):
                # Read existing Excel file
                existing_df = pd.read_excel(excel_path)
                # Concatenate with new data
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                # Save back to Excel
                combined_df.to_excel(excel_path, index=False)
            else:
                # Create new Excel file
                new_df.to_excel(excel_path, index=False)
                
            logger.info("Data stored in Excel successfully")
        except Exception as excel_error:
            logger.error(f"Error storing data in Excel: {str(excel_error)}")
            # Continue even if Excel storage fails
        
        # Get assessment results for the certificate and UI
        try:
            logger.info("Calculating assessment results...")
            assessment_results = evaluate_responses(responses)
            logger.info("Assessment calculation completed")
        except Exception as assessment_error:
            logger.error(f"Error in assessment calculation: {str(assessment_error)}")
            assessment_results = {
                'technical': {'percentage': 0, 'indicators': {}},
                'social': {'percentage': 0, 'indicators': {}},
                'overall': {'percentage': 0, 'level': 'Error'}
            }
        
        # Get recommendations for display in the UI
        try:
            logger.info("Getting AI recommendations...")
            recommendations = analyze_responses(personal_data, responses)
            logger.info("AI recommendations completed")
        except Exception as ai_error:
            logger.error(f"Error getting AI recommendations: {str(ai_error)}")
            recommendations = "Error generating recommendations. Please try again later."
        
        # Generate certificate
        try:
            logger.info("Generating certificate...")
            certificate_path = generate_certificate(personal_data, responses)
            logger.info(f"Certificate generated: {certificate_path}")
        except Exception as cert_error:
            logger.error(f"Error generating certificate: {str(cert_error)}")
            logger.error(f"Certificate error details: {traceback.format_exc()}")
            return jsonify({'status': 'error', 'message': f'Error generating certificate: {str(cert_error)}'}), 500
        
        # Return success response
        logger.info("Returning successful response to client")
        return jsonify({
            'status': 'success',
            'certificate_path': certificate_path,
            'recommendations': recommendations,
            'assessment': assessment_results
        })
        
    except Exception as e:
        logger.error(f"Error in submit_questionnaire: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/download_certificate/<filename>')
def download_certificate(filename):
    logger.info(f"Downloading certificate: {filename}")
    
    # Handle the error certificate case
    if filename == "certificate_error.pdf":
        logger.warning("Attempting to download error certificate placeholder")
        return jsonify({
            'status': 'error',
            'message': 'Sertifikat tidak dapat dibuat. Silakan coba lagi.'
        }), 404
    
    # Check if the certificate file exists
    cert_path = os.path.join('certificates', filename)
    if not os.path.exists(cert_path):
        logger.error(f"Certificate file not found: {cert_path}")
        
        # Try to find the HTML version instead
        html_path = cert_path.replace('.pdf', '.html')
        if os.path.exists(html_path):
            logger.info(f"Found HTML version of certificate: {html_path}")
            return send_file(html_path, as_attachment=True, download_name=filename.replace('.pdf', '.html'))
        
        return jsonify({
            'status': 'error',
            'message': 'Sertifikat tidak ditemukan. Silakan coba lagi.'
        }), 404
    
    try:
        logger.info(f"Sending certificate file: {cert_path}")
        return send_file(cert_path, as_attachment=True)
    except Exception as e:
        logger.error(f"Error sending certificate file: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error saat mengirim sertifikat: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Cybersecurity Awareness Assessment Server...")
    print("💻 Open http://127.0.0.1:5000 in your browser")
    app.run(host='0.0.0.0', port=5000, debug=True) 