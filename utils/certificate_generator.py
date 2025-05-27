from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
import os
import logging
import traceback
from datetime import datetime
from utils.ai_analyzer import analyze_responses, get_llm_response
from utils.assessment_evaluator import evaluate_responses
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('certificate-generator')

def generate_interpretation(results):
    """Generate detailed interpretation of assessment results using LLM"""
    try:
        logger.info("Generating interpretation using LLM...")
        
        # Prepare data for LLM
        assessment_data = {
            'overall': {
                'level': results['overall']['level'],
                'percentage': results['overall']['percentage']
            },
            'technical': {
                'percentage': results['technical']['percentage'],
                'indicators': results['technical']['indicators']
            },
            'social': {
                'percentage': results['social']['percentage'],
                'indicators': results['social']['indicators']
            }
        }
        
        # Create prompt for LLM
        prompt = f"""Berdasarkan hasil penilaian kesadaran keamanan siber berikut, berikan interpretasi yang komprehensif:

Hasil Keseluruhan:
- Tingkat Kesadaran: {assessment_data['overall']['level']} ({assessment_data['overall']['percentage']:.1f}%)
- Kesadaran Teknis: {assessment_data['technical']['percentage']:.1f}%
- Kesadaran Sosial: {assessment_data['social']['percentage']:.1f}%

Detail Indikator Teknis:
{chr(10).join([f"- {indicator}: {data['percentage']:.1f}%" for indicator, data in assessment_data['technical']['indicators'].items()])}

Detail Indikator Sosial:
{chr(10).join([f"- {indicator}: {data['percentage']:.1f}%" for indicator, data in assessment_data['social']['indicators'].items()])}

Berdasarkan data di atas, berikan interpretasi yang mencakup:
1. Analisis keseluruhan tingkat kesadaran
2. Analisis detail untuk setiap indikator teknis dan sosial
3. Identifikasi kekuatan dan area yang perlu ditingkatkan
4. Rekomendasi spesifik untuk peningkatan

Format interpretasi:
- Gunakan bahasa yang profesional namun mudah dipahami
- Berikan contoh konkret untuk setiap poin
- Fokus pada aspek praktis yang dapat diterapkan
- Berikan saran yang spesifik dan actionable
"""

        # Get interpretation from LLM
        interpretation = get_llm_response(prompt)
        
        # Extract strengths and weaknesses from interpretation
        strengths = []
        weaknesses = []
        
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
        
    except Exception as e:
        logger.error(f"Error generating interpretation: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Fallback to basic interpretation if LLM fails
        basic_interpretation = f"""Hasil penilaian kesadaran keamanan siber menunjukkan tingkat {results['overall']['level']} ({results['overall']['percentage']:.1f}%).

Kesadaran Teknis: {results['technical']['percentage']:.1f}%
Kesadaran Sosial: {results['social']['percentage']:.1f}%

Detail indikator dapat dilihat pada tabel di halaman sebelumnya."""
        
        return basic_interpretation, [], []

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
        
        # Generate interpretation
        interpretation, strengths, weaknesses = generate_interpretation(assessment_results)
        
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
            'detailed_analysis': ai_analysis
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

def generate_certificate_with_template(
    personal_data, 
    assessment_results, 
    output_basename="certificate"
):
    """
    Generate certificate using PNG template, write data, save as PNG and PDF.
    Args:
        personal_data: dict, must contain 'name'
        assessment_results: dict, must contain 'technical', 'social', 'overall', and indicator scores
        output_basename: str, base filename (without extension)
    Returns:
        (png_path, pdf_path)
    """
    # Path setup
    template_path = os.path.join("certificate_template", "certificate_template.png")
    output_dir = "certificates"
    os.makedirs(output_dir, exist_ok=True)
    png_path = os.path.join(output_dir, f"{output_basename}.png")
    pdf_path = os.path.join(output_dir, f"{output_basename}.pdf")

    # Load template
    image = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(image)

    # Load fonts
    font_lucida = os.path.join(os.path.dirname(__file__), '..', 'Lucida Calligraphy Font.ttf')
    font_montserrat = os.path.join(os.path.dirname(__file__), '..', 'Montserrat-Regular.ttf')
    if os.path.exists(font_lucida):
        font_nama = ImageFont.truetype(font_lucida, 70)
    else:
        font_nama = ImageFont.load_default()
    if os.path.exists(font_montserrat):
        font_angka = ImageFont.truetype(font_montserrat, 22)
        font_angka_besar = ImageFont.truetype(font_montserrat, 22)
        font_angka_kks = ImageFont.truetype(font_montserrat, 24)
    else:
        font_angka = ImageFont.load_default()
        font_angka_besar = ImageFont.load_default()
        font_angka_kks = ImageFont.load_default()

    # Konversi nilai ke skala 1-100 dengan 2 digit desimal
    def to_scale_100(val):
        return round(float(val), 2)

    # Nama (Lucida Calligraphy, rata tengah)
    nama = personal_data.get("name", "")
    bbox_nama = font_nama.getbbox(nama)
    w_nama = bbox_nama[2] - bbox_nama[0]
    x_nama = (image.width - w_nama) // 2
    draw.text((x_nama, 325), nama, fill="black", font=font_nama)

    # Predikat (Montserrat, rata tengah)
    predikat = assessment_results['overall']['level']
    bbox_predikat = font_angka.getbbox(predikat)
    w_predikat = bbox_predikat[2] - bbox_predikat[0]
    x_predikat = (image.width - w_predikat) // 2
    draw.text((x_predikat, 475), predikat, fill="black", font=font_angka)

    # Nilai individu (Montserrat, rata tengah)
    nilai_individu = f"{to_scale_100(assessment_results['overall']['percentage']):.2f}"
    bbox_individu = font_angka.getbbox(nilai_individu)
    w_individu = bbox_individu[2] - bbox_individu[0]
    x_individu = (image.width - w_individu) // 2
    draw.text((x_individu, 533), nilai_individu, fill="black", font=font_angka)

    # Nilai teknis & sosial (Montserrat 44)
    draw.text((280, 585), f"{to_scale_100(assessment_results['technical']['percentage']):.2f}", fill="black", font=font_angka_kks)
    draw.text((580, 585), f"{to_scale_100(assessment_results['social']['percentage']):.2f}", fill="black", font=font_angka_kks)

    # Skor indikator teknis (Montserrat 22)
    teknis_y_map = [679, 726, 770, 813, 858, 898]
    for idx, (indikator, nilai) in enumerate(assessment_results['technical']['indicators'].items()):
        nilai_angka = nilai['percentage'] if isinstance(nilai, dict) and 'percentage' in nilai else nilai
        draw.text((283, teknis_y_map[idx]), f"{to_scale_100(nilai_angka):.2f}", fill="black", font=font_angka_besar)

    # Skor indikator sosial (Montserrat 22)
    sosial_y_map = [677, 721, 764, 808, 851]
    for idx, (indikator, nilai) in enumerate(assessment_results['social']['indicators'].items()):
        nilai_angka = nilai['percentage'] if isinstance(nilai, dict) and 'percentage' in nilai else nilai
        draw.text((583, sosial_y_map[idx]), f"{to_scale_100(nilai_angka):.2f}", fill="black", font=font_angka_besar)

    # Simpan PNG
    image.save(png_path)

    # Konversi ke PDF dengan orientasi sesuai gambar
    width, height = image.size
    orientation = 'P' if height >= width else 'L'
    pdf = FPDF(orientation=orientation, unit='pt', format=(width, height))
    pdf.add_page()
    pdf.image(png_path, 0, 0, width, height)
    pdf.output(pdf_path)

    return png_path, pdf_path 