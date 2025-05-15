import pandas as pd
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('assessment-evaluator')

# Define the structure of indicators based on hasil-skks-page1.xlsx
TECHNICAL_INDICATORS = {
    "Syarat dan Ketentuan Instalasi Perangkat/Aplikasi": [1, 2],
    "Kata Sandi (Password)": [3, 4, 5, 6, 7, 8],
    "Internet dan Wifi": [9, 10, 11, 12, 13],
    "Keamanan Perangkat": [14, 15, 16, 17, 18, 19],
    "Aduan Insiden Siber Teknis": [20, 21, 22],
    "Hukum dan Regulasi Keamanan Siber Teknis": [23, 24]
}

SOCIAL_INDICATORS = {
    "Rekayasa Sosial (Social Engineering)": [25, 26, 27, 28, 29, 30],
    "Konten Negatif": [31, 32, 33],
    "Aktivitas Media Sosial": [34, 35, 36, 37, 38],
    "Aduan Insiden Siber Sosial": [39, 40, 41],
    "Hukum dan Regulasi Keamanan Siber Sosial": [42, 43]
}

def evaluate_responses(responses):
    """
    Evaluate questionnaire responses according to the reference structure
    
    Args:
        responses: Dictionary of responses where keys are question IDs (q1, q2, etc.) and values are scores (1-4)
        
    Returns:
        Dictionary containing detailed assessment results
    """
    try:
        logger.info(f"Starting assessment evaluation with {len(responses)} responses")
        
        # Convert responses to a format where keys are question numbers (1, 2, 3, etc.)
        numeric_responses = {}
        for key, value in responses.items():
            if key.startswith('q'):
                try:
                    question_num = int(key[1:])
                    numeric_responses[question_num] = int(value)
                except (ValueError, IndexError):
                    logger.warning(f"Invalid question ID format: {key}")
                    continue
        
        logger.info(f"Processed {len(numeric_responses)} valid responses")
        
        # Calculate scores for each technical indicator
        technical_scores = {}
        for indicator, questions in TECHNICAL_INDICATORS.items():
            try:
                indicator_scores = [numeric_responses.get(q, 0) for q in questions]
                valid_scores = [s for s in indicator_scores if s > 0]
                
                if not valid_scores:
                    logger.warning(f"No valid responses for indicator: {indicator}")
                    avg_score = 0
                else:
                    avg_score = sum(valid_scores) / len(valid_scores)
                
                technical_scores[indicator] = {
                    'score': avg_score,
                    'percentage': (avg_score / 4) * 100  # 4 is max score per question
                }
            except Exception as e:
                logger.error(f"Error calculating score for technical indicator {indicator}: {str(e)}")
                technical_scores[indicator] = {'score': 0, 'percentage': 0}
        
        # Calculate scores for each social indicator
        social_scores = {}
        for indicator, questions in SOCIAL_INDICATORS.items():
            try:
                indicator_scores = [numeric_responses.get(q, 0) for q in questions]
                valid_scores = [s for s in indicator_scores if s > 0]
                
                if not valid_scores:
                    logger.warning(f"No valid responses for indicator: {indicator}")
                    avg_score = 0
                else:
                    avg_score = sum(valid_scores) / len(valid_scores)
                
                social_scores[indicator] = {
                    'score': avg_score,
                    'percentage': (avg_score / 4) * 100  # 4 is max score per question
                }
            except Exception as e:
                logger.error(f"Error calculating score for social indicator {indicator}: {str(e)}")
                social_scores[indicator] = {'score': 0, 'percentage': 0}
        
        # Calculate variable scores
        try:
            technical_avg = sum(item['score'] for item in technical_scores.values()) / len(technical_scores) if technical_scores else 0
            social_avg = sum(item['score'] for item in social_scores.values()) / len(social_scores) if social_scores else 0
        except Exception as e:
            logger.error(f"Error calculating average scores: {str(e)}")
            technical_avg = 0
            social_avg = 0
        
        # Calculate overall score
        overall_score = (technical_avg + social_avg) / 2
        overall_percentage = (overall_score / 4) * 100  # 4 is max score
        
        # Determine awareness level
        awareness_level = "Buruk"
        if overall_percentage >= 80:
            awareness_level = "Sangat Baik"
        elif overall_percentage >= 50:
            awareness_level = "Baik"
        elif overall_percentage >= 25:
            awareness_level = "Kurang Baik"
        
        logger.info(f"Assessment completed - Overall Score: {overall_percentage:.1f}%, Level: {awareness_level}")
        
        # Prepare the final results
        results = {
            'technical': {
                'indicators': technical_scores,
                'average_score': technical_avg,
                'percentage': (technical_avg / 4) * 100
            },
            'social': {
                'indicators': social_scores,
                'average_score': social_avg,
                'percentage': (social_avg / 4) * 100
            },
            'overall': {
                'score': overall_score,
                'percentage': overall_percentage,
                'level': awareness_level
            }
        }
        
        return results
        
    except Exception as e:
        logger.error(f"Error in assessment evaluation: {str(e)}")
        
        # Return a minimal fallback result
        return {
            'technical': {
                'indicators': {},
                'average_score': 0,
                'percentage': 0
            },
            'social': {
                'indicators': {},
                'average_score': 0,
                'percentage': 0
            },
            'overall': {
                'score': 0,
                'percentage': 0,
                'level': 'Error'
            }
        } 