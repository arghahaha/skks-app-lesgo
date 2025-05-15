# Cybersecurity Awareness Assessment Service

A web-based application for assessing cybersecurity awareness levels using questionnaires and providing personalized recommendations.

## Features

- Personal data collection
- Cybersecurity awareness questionnaire with Likert scale responses
- Excel database storage for responses
- Automated certificate generation using WeasyPrint
- Personalized cybersecurity recommendations using GPT-4-mini
- Context-based and role-based prompting for recommendations

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

4. Run the application:
```bash
python app.py
```

## Project Structure

- `app.py`: Main application file
- `templates/`: HTML templates
- `static/`: CSS, JavaScript, and other static files
- `data/`: Excel database storage
- `certificates/`: Generated certificates
- `utils/`: Utility functions for certificate generation and AI analysis 