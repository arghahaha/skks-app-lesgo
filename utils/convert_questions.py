import json
import pandas as pd

def convert_json_to_excel():
    try:
        # Read questions from JSON
        with open('data/questions.json', 'r', encoding='utf-8') as f:
            questions_data = json.load(f)

        # Convert to DataFrame format
        questions = []
        for i, q in enumerate(questions_data['questions'], 1):
            questions.append({
                'id': i,
                'question': q['text'],
                'category': q['category']
            })

        # Create DataFrame
        df = pd.DataFrame(questions)

        # Save to Excel
        df.to_excel('data/question.xlsx', index=False)
        print("Questions have been converted and saved to question.xlsx")
        
    except Exception as e:
        print(f"Error converting questions: {str(e)}")
        raise

if __name__ == "__main__":
    convert_json_to_excel() 