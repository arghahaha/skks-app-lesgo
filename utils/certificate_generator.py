from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
import os
import logging
import traceback
from datetime import datetime
from utils.ai_analyzer import analyze_responses
from utils.assessment_evaluator import evaluate_responses

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('certificate-generator')

def generate_interpretation(results):
    """Generate detailed interpretation of assessment results"""
    interpretation = ""
    strengths = []
    weaknesses = []
    
    # Interpret overall level
    level = results['overall']['level']
    percentage = results['overall']['percentage']
    
    if level == "Sangat Baik":
        interpretation = f"Berdasarkan hasil penilaian, Anda memiliki tingkat kesadaran keamanan siber yang sangat baik ({percentage:.1f}%). "
        interpretation += "Anda menunjukkan pemahaman yang komprehensif terhadap aspek teknis dan sosial dari keamanan siber."
    elif level == "Baik":
        interpretation = f"Hasil penilaian menunjukkan tingkat kesadaran keamanan siber yang baik ({percentage:.1f}%). "
        interpretation += "Anda memiliki pemahaman yang cukup baik tentang keamanan siber, namun masih ada beberapa area yang dapat ditingkatkan."
    elif level == "Kurang Baik":
        interpretation = f"Tingkat kesadaran keamanan siber Anda berada pada kategori kurang baik ({percentage:.1f}%). "
        interpretation += "Beberapa aspek keamanan siber perlu mendapat perhatian lebih untuk meningkatkan kesadaran Anda."
    else:
        interpretation = f"Tingkat kesadaran keamanan siber Anda berada pada kategori buruk ({percentage:.1f}%). "
        interpretation += "Penting untuk meningkatkan pemahaman dan praktik keamanan siber Anda."

    # Analyze technical indicators
    for indicator, data in results['technical']['indicators'].items():
        if data['percentage'] >= 75:
            strengths.append(f"Memiliki pemahaman yang baik tentang {indicator}")
        elif data['percentage'] < 50:
            weaknesses.append(f"Perlu meningkatkan pemahaman tentang {indicator}")

    # Analyze social indicators
    for indicator, data in results['social']['indicators'].items():
        if data['percentage'] >= 75:
            strengths.append(f"Memiliki kesadaran yang baik tentang {indicator}")
        elif data['percentage'] < 50:
            weaknesses.append(f"Perlu meningkatkan kesadaran tentang {indicator}")

    return interpretation, strengths, weaknesses

def generate_recommendations(results, personal_data):
    """Generate personalized recommendations based on assessment results"""
    general_recommendations = []
    technical_recommendations = []
    social_recommendations = []
    implementation_steps = []

    # General recommendations based on overall level
    level = results['overall']['level']
    if level == "Sangat Baik":
        general_recommendations = [
            "Pertahankan dan tingkatkan praktik keamanan siber yang sudah baik",
            "Bagikan pengetahuan keamanan siber dengan orang lain",
            "Ikuti perkembangan terbaru dalam bidang keamanan siber"
        ]
    elif level == "Baik":
        general_recommendations = [
            "Tingkatkan pemahaman tentang praktik keamanan siber terbaik",
            "Ikuti pelatihan keamanan siber secara berkala",
            "Terapkan praktik keamanan siber dalam aktivitas sehari-hari"
        ]
    elif level == "Kurang Baik":
        general_recommendations = [
            "Mulai mempelajari dasar-dasar keamanan siber",
            "Ikuti pelatihan keamanan siber dasar",
            "Terapkan langkah-langkah keamanan dasar dalam aktivitas digital"
        ]
    else:
        general_recommendations = [
            "Mulai mempelajari konsep dasar keamanan siber",
            "Ikuti pelatihan keamanan siber dasar",
            "Terapkan langkah-langkah keamanan dasar dalam aktivitas digital"
        ]

    # Technical recommendations
    for indicator, data in results['technical']['indicators'].items():
        if data['percentage'] < 75:
            if indicator == "Kata Sandi (Password)":
                technical_recommendations.append("Gunakan kata sandi yang kuat dan unik untuk setiap akun")
            elif indicator == "Internet dan Wifi":
                technical_recommendations.append("Hindari menggunakan wifi publik untuk aktivitas sensitif")
            elif indicator == "Keamanan Perangkat":
                technical_recommendations.append("Aktifkan fitur keamanan pada perangkat Anda")
            elif indicator == "Aduan Insiden Siber Teknis":
                technical_recommendations.append("Pelajari cara melaporkan insiden keamanan siber")
            elif indicator == "Hukum dan Regulasi Keamanan Siber Teknis":
                technical_recommendations.append("Pelajari regulasi keamanan siber yang berlaku")

    # Social recommendations
    for indicator, data in results['social']['indicators'].items():
        if data['percentage'] < 75:
            if indicator == "Rekayasa Sosial (Social Engineering)":
                social_recommendations.append("Waspadai upaya manipulasi melalui media digital")
            elif indicator == "Konten Negatif":
                social_recommendations.append("Verifikasi informasi sebelum membagikannya")
            elif indicator == "Aktivitas Media Sosial":
                social_recommendations.append("Batasi informasi pribadi yang dibagikan di media sosial")
            elif indicator == "Aduan Insiden Siber Sosial":
                social_recommendations.append("Pelajari cara melaporkan konten negatif")
            elif indicator == "Hukum dan Regulasi Keamanan Siber Sosial":
                social_recommendations.append("Pelajari regulasi terkait aktivitas digital")

    # Implementation steps
    implementation_steps = [
        "Buat daftar prioritas berdasarkan rekomendasi di atas",
        "Tentukan jadwal untuk menerapkan setiap rekomendasi",
        "Cari sumber daya pembelajaran yang sesuai dengan tingkat pendidikan Anda",
        "Terapkan rekomendasi secara bertahap dan konsisten",
        "Evaluasi kemajuan secara berkala"
    ]

    return {
        'general_recommendations': general_recommendations,
        'technical_recommendations': technical_recommendations,
        'social_recommendations': social_recommendations,
        'implementation_steps': implementation_steps
    }

def generate_certificate(personal_data, responses):
    """
    Generate a PDF certificate with assessment results and recommendations
    
    Args:
        personal_data: Dictionary containing personal information
        responses: Dictionary containing questionnaire responses
        
    Returns:
        String containing the filename of the generated certificate
    """
    try:
        logger.info("Starting certificate generation...")
        
        # Create a fallback filename in case of errors
        filename = f"certificate_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{personal_data['name'].replace(' ', '_')}.pdf"
        output_path = os.path.join('certificates', filename)
        
        # Create Jinja2 environment
        env = Environment(loader=FileSystemLoader('templates'))
        
        # Get detailed assessment results
        logger.info("Getting assessment results...")
        assessment_results = evaluate_responses(responses)
        
        # Get AI analysis and recommendations
        logger.info("Getting AI analysis and recommendations...")
        ai_analysis = analyze_responses(personal_data, responses)
        
        # Parse AI analysis into sections
        sections = ai_analysis.split('\n\n')
        interpretation = ""
        strengths = []
        weaknesses = []
        general_recommendations = []
        technical_recommendations = []
        social_recommendations = []
        implementation_steps = []
        
        current_section = None
        for section in sections:
            if "TINDAKAN PENTING" in section:
                current_section = "tindakan"
                technical_recommendations.extend([line.strip('- ') for line in section.split('\n') if line.strip().startswith('-')])
            elif "PENGUATAN KEAMANAN" in section:
                current_section = "penguatan"
                general_recommendations.extend([line.strip('- ') for line in section.split('\n') if line.strip().startswith('-')])
            elif "PELATIHAN & PENGEMBANGAN" in section:
                current_section = "pelatihan"
                implementation_steps.extend([line.strip('- ') for line in section.split('\n') if line.strip().startswith('-')])
            elif "ALAT & SUMBER DAYA" in section:
                current_section = "alat"
                technical_recommendations.extend([line.strip('- ') for line in section.split('\n') if line.strip().startswith('-')])
            elif current_section == "tindakan":
                weaknesses.append(section.strip())
            elif current_section == "penguatan":
                strengths.append(section.strip())
        
        # Generate interpretation based on assessment results and AI analysis
        interpretation = f"Berdasarkan hasil penilaian, Anda memiliki tingkat kesadaran keamanan siber {assessment_results['overall']['level'].lower()} ({assessment_results['overall']['percentage']:.1f}%). "
        interpretation += f"Skor kesadaran teknis Anda adalah {assessment_results['technical']['percentage']:.1f}% dan kesadaran sosial {assessment_results['social']['percentage']:.1f}%. "
        
        # Add AI-generated interpretation
        if ai_analysis:
            interpretation += "\n\n" + ai_analysis.split('\n\n')[0] if ai_analysis else ""
        
        # Format the detailed assessment for better display
        technical_indicators = []
        for name, data in assessment_results['technical']['indicators'].items():
            technical_indicators.append({
                'name': name,
                'percentage': f"{data['percentage']:.1f}%"
            })
        
        social_indicators = []
        for name, data in assessment_results['social']['indicators'].items():
            social_indicators.append({
                'name': name,
                'percentage': f"{data['percentage']:.1f}%"
            })
        
        # Prepare certificate data
        certificate_data = {
            'name': personal_data['name'],
            'date': datetime.now().strftime('%d %B %Y'),
            'education': personal_data['education'],
            'domicile': personal_data['domicile'],
            'technical_score': f"{assessment_results['technical']['percentage']:.1f}%",
            'social_score': f"{assessment_results['social']['percentage']:.1f}%",
            'overall_score': f"{assessment_results['overall']['percentage']:.1f}%",
            'awareness_level': assessment_results['overall']['level'],
            'technical_indicators': technical_indicators,
            'social_indicators': social_indicators,
            'interpretation': interpretation,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'detailed_analysis': ai_analysis,
            'general_recommendations': general_recommendations,
            'technical_recommendations': technical_recommendations,
            'social_recommendations': social_recommendations,
            'implementation_steps': implementation_steps
        }
        
        # Render template
        logger.info("Rendering certificate template...")
        template = env.get_template('certificate.html')
        html_content = template.render(**certificate_data)
        
        # Create certificates directory if it doesn't exist
        os.makedirs('certificates', exist_ok=True)
        
        # Save the HTML for debugging if needed
        debug_html_path = output_path.replace('.pdf', '.html')
        with open(debug_html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"Saved debug HTML to: {debug_html_path}")
        
        # Create HTML and CSS objects with simplest possible styling
        logger.info("Creating HTML and CSS objects...")
        html = HTML(string=html_content)
        css = CSS(string='@page { size: A4; margin: 1cm; }')
        
        try:
            # Write PDF with CSS
            logger.info("Writing PDF file...")
            html.write_pdf(output_path, stylesheets=[css])
            logger.info(f"Certificate generated successfully: {filename}")
            return filename
        except Exception as pdf_error:
            logger.error(f"Error writing PDF: {str(pdf_error)}")
            logger.error(traceback.format_exc())
            
            # Try with even simpler CSS
            try:
                logger.info("Retrying with simpler CSS...")
                simple_css = CSS(string='@page { margin: 1cm; }')
                html.write_pdf(output_path, stylesheets=[simple_css])
                logger.info(f"Certificate generated with fallback CSS: {filename}")
                return filename
            except Exception as simple_pdf_error:
                logger.error(f"Error with simple CSS: {str(simple_pdf_error)}")
                
                # Try with no CSS
                try:
                    logger.info("Retrying with no CSS...")
                    html.write_pdf(output_path)
                    logger.info(f"Certificate generated with no CSS: {filename}")
                    return filename
                except Exception as no_css_error:
                    logger.error(f"Error with no CSS: {str(no_css_error)}")
                    raise
        
    except Exception as e:
        logger.error(f"Error generating certificate: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Return a default certificate name to prevent UI errors
        return "certificate_error.pdf" 