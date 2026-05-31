import os
import re
import zlib
import base64
import warnings
import httpx
from fpdf import FPDF

# Suppress fpdf2 deprecation warnings to ensure clean output across versions
warnings.filterwarnings("ignore", category=DeprecationWarning)

class CustomPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("helvetica", "I", 8)
            self.set_text_color(100, 100, 100)
            self.cell(90, 10, "Buscador Biografico Inteligente - Dra. Nassara Mesquita", border=0)
            self.cell(0, 10, "Plano de Implementacao", border=0, align="R")
            self.ln(8)
            # Thin gold line
            self.set_draw_color(197, 168, 128)
            self.set_line_width(0.5)
            self.line(10, 20, 200, 20)
            self.ln(4)

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font("helvetica", "I", 8)
            self.set_text_color(100, 100, 100)
            self.set_draw_color(197, 168, 128)
            self.set_line_width(0.5)
            self.line(10, 280, 200, 280)
            self.cell(0, 10, f"Pagina {self.page_no()}", border=0, align="C")

def clean_text(text):
    text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    text = text.replace("—", "-").replace("–", "-")
    text = text.replace("•", "-")
    text = text.replace("º", "o").replace("ª", "a")
    text = text.replace("Nássara", "Nassara")
    
    try:
        text.encode("latin-1")
    except UnicodeEncodeError:
        text = text.encode("latin-1", errors="replace").decode("latin-1")
    return text

def download_mermaid_image(mermaid_code, index):
    """
    Downloads rendered PNG of the Mermaid code from Kroki.io.
    Uses Zlib compression and URL-safe Base64 encoding.
    Forces theme: dark to match the user's VS Code aesthetics perfectly.
    """
    print(f"Renderizando diagrama Mermaid {index} via Kroki + Zlib...")
    
    # Strip whitespace lines
    cleaned_code = "\n".join([line for line in mermaid_code.split("\n") if line.strip()])
    
    # Inject dark theme configuration directive in the Mermaid diagram code
    # This is compatible with all modern Mermaid renderers
    if "%%{init" not in cleaned_code:
        theme_directive = "%%{init: {'theme': 'dark', 'themeVariables': {'background': '#121212', 'primaryColor': '#c5a880', 'lineColor': '#c5a880'}}}%%\n"
        cleaned_code = theme_directive + cleaned_code
        
    try:
        # Kroki.io official encoding standard:
        # 1. Encode text as UTF-8
        # 2. Compress using zlib (deflate)
        # 3. Base64 encode using URL-safe alphabet
        compressed = zlib.compress(cleaned_code.encode("utf-8"), 9)
        b64_kroki = base64.urlsafe_b64encode(compressed).decode("utf-8")
        
        url_kroki = f"https://kroki.io/mermaid/png/{b64_kroki}"
        
        temp_filename = f"temp_mermaid_{index}.png"
        
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url_kroki)
            if response.status_code == 200 and len(response.content) > 1000:
                with open(temp_filename, "wb") as f:
                    f.write(response.content)
                print(f"Diagrama {index} baixado com sucesso via Kroki!")
                return temp_filename
            else:
                print(f"Erro na API Kroki (Status {response.status_code}) para o diagrama {index}.")
    except Exception as e:
        print(f"Falha ao baixar imagem do Mermaid via Kroki: {e}")
        
    return None

def create_pdf(md_path, pdf_path):
    pdf = CustomPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(15, 20, 15)
    pdf.set_auto_page_break(auto=True, margin=20)
    
    # ── COVER PAGE ──
    pdf.add_page()
    
    # Decorative Top Bar (Dark Blue)
    pdf.set_fill_color(13, 27, 42)
    pdf.rect(0, 0, 210, 40, "F")
    
    # Gold Highlight Line
    pdf.set_fill_color(197, 168, 128)
    pdf.rect(0, 40, 210, 4, "F")
    
    pdf.ln(50)
    
    # Project Title
    pdf.set_font("helvetica", "B", 24)
    pdf.set_text_color(13, 27, 42)
    pdf.multi_cell(0, 12, "BUSCADOR BIOGRAFICO INTELIGENTE", align="C")
    
    # Subtitle
    pdf.ln(5)
    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(197, 168, 128) # Gold
    pdf.cell(0, 10, "Dra. Nassara Mesquita", ln=True, align="C")
    
    # Document Title
    pdf.ln(15)
    pdf.set_font("helvetica", "", 14)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 10, "PLANO DE IMPLEMENTACAO E ARQUITETURA", ln=True, align="C")
    
    # Decorative center line
    pdf.ln(10)
    pdf.set_draw_color(197, 168, 128)
    pdf.set_line_width(1)
    pdf.line(70, pdf.get_y(), 140, pdf.get_y())
    
    # Metadata block at bottom
    pdf.set_y(-60)
    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(13, 27, 42)
    pdf.cell(0, 6, "CLIENTE:", ln=True, align="C")
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 6, "Dra. Nassara Mesquita - Goiania/GO", ln=True, align="C")
    
    pdf.ln(4)
    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(13, 27, 42)
    pdf.cell(0, 6, "TECNOLOGIAS:", ln=True, align="C")
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 6, "FastAPI Pro, SQLite, Multi-Agent System, Glassmorphic UI", ln=True, align="C")
    
    pdf.ln(4)
    pdf.set_font("helvetica", "I", 9)
    pdf.cell(0, 6, "Data de Geracao: 31 de Maio de 2026", ln=True, align="C")
    
    # ── READ & PARSE CONTENT ──
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Remove frontmatter
    content = re.sub(r"^---.*?---", "", content, flags=re.DOTALL)
    
    # Extract all Mermaid blocks and download their PNG representations
    mermaid_blocks = re.findall(r"```mermaid\s*\n(.*?)\n```", content, re.DOTALL)
    mermaid_images = {}
    
    for idx, block in enumerate(mermaid_blocks, start=1):
        img_path = download_mermaid_image(block, idx)
        if img_path:
            mermaid_images[idx] = img_path
            
    # Clean document text to latin-1
    content = clean_text(content)
    
    # Split back to lines
    lines = content.split("\n")
    
    in_mermaid = False
    in_code = False
    mermaid_counter = 0
    
    # ── CONTENT PAGES ──
    pdf.add_page()
    
    for line in lines:
        stripped = line.strip()
        
        # Handle Mermaid blocks
        if stripped.startswith("```mermaid"):
            in_mermaid = True
            mermaid_counter += 1
            pdf.ln(4)
            continue
            
        if in_mermaid:
            if stripped.startswith("```"):
                in_mermaid = False
                # Insert the pre-downloaded Mermaid PNG image
                img_file = mermaid_images.get(mermaid_counter)
                if img_file and os.path.exists(img_file):
                    # Align and insert image (180mm width fits within 210mm A4 page with margins)
                    pdf.image(img_file, w=180)
                    pdf.ln(5)
                else:
                    pdf.set_font("helvetica", "I", 9)
                    pdf.set_text_color(150, 50, 50)
                    pdf.cell(0, 6, "[Falha ao renderizar diagrama do Mermaid]", ln=True)
                continue
            # Skip outputting the textual mermaid code
            continue
            
        # Handle code blocks
        if stripped.startswith("```"):
            if in_code:
                in_code = False
                pdf.ln(3)
            else:
                in_code = True
                pdf.set_fill_color(245, 245, 245)
                pdf.set_font("courier", "", 9)
                pdf.set_text_color(60, 60, 60)
            continue
            
        if in_code:
            pdf.cell(0, 5, line, ln=True, fill=True)
            continue
            
        # Headers
        if stripped.startswith("# "):
            title = stripped[2:]
            pdf.ln(8)
            pdf.set_font("helvetica", "B", 18)
            pdf.set_text_color(13, 27, 42)
            pdf.cell(0, 10, title, ln=True)
            pdf.set_draw_color(197, 168, 128)
            pdf.set_line_width(0.7)
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 50, pdf.get_y())
            pdf.ln(4)
            continue
            
        if stripped.startswith("## "):
            title = stripped[3:]
            pdf.ln(6)
            pdf.set_font("helvetica", "B", 13)
            pdf.set_text_color(13, 27, 42)
            pdf.cell(0, 8, title, ln=True)
            pdf.ln(2)
            continue
            
        if stripped.startswith("### "):
            title = stripped[4:]
            pdf.ln(4)
            pdf.set_font("helvetica", "B", 11)
            pdf.set_text_color(197, 168, 128)
            pdf.cell(0, 6, title, ln=True)
            pdf.ln(1)
            continue
            
        # Bullet list items
        if stripped.startswith("* ") or stripped.startswith("- "):
            bullet_text = stripped[2:]
            pdf.set_font("helvetica", "", 10)
            pdf.set_text_color(50, 50, 50)
            
            pdf.set_x(20)
            pdf.write(5, "- ")
            
            parts = re.split(r"(\*\*.*?\*\*)", bullet_text)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    pdf.set_font("helvetica", "B", 10)
                    pdf.write(5, part[2:-2])
                else:
                    pdf.set_font("helvetica", "", 10)
                    pdf.write(5, part)
            pdf.ln(6)
            continue
            
        # Table rows or delimiters
        if stripped.startswith("|"):
            if "---" in stripped:
                continue
            cols = [c.strip() for c in stripped.split("|")[1:-1]]
            pdf.set_fill_color(240, 243, 246)
            pdf.set_font("helvetica", "B" if "Agente" in stripped or "Resultado" in stripped or "Criterio" in stripped or "Campo" in stripped else "", 9)
            pdf.set_text_color(50, 50, 50)
            
            if len(cols) >= 3:
                pdf.cell(40, 7, cols[0], border=1, fill=True)
                pdf.cell(60, 7, cols[1], border=1, fill=True)
                pdf.cell(80, 7, cols[2], border=1, fill=True)
                pdf.ln(7)
            elif len(cols) == 2:
                pdf.cell(60, 7, cols[0], border=1, fill=True)
                pdf.cell(120, 7, cols[1], border=1, fill=True)
                pdf.ln(7)
            continue

        # Regular paragraph
        if stripped:
            pdf.set_font("helvetica", "", 10)
            pdf.set_text_color(50, 50, 50)
            
            parts = re.split(r"(\*\*.*?\*\*)", line)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    pdf.set_font("helvetica", "B", 10)
                    pdf.write(5, part[2:-2])
                else:
                    pdf.set_font("helvetica", "", 10)
                    pdf.write(5, part)
            pdf.ln(6)
        else:
            pdf.ln(2)

    # Save PDF
    pdf.output(pdf_path)
    print(f"PDF gerado com sucesso em: {pdf_path}")
    
    # ── CLEAN UP TEMPORARY IMAGES ──
    for img_file in mermaid_images.values():
        try:
            if os.path.exists(img_file):
                os.remove(img_file)
        except Exception:
            pass

if __name__ == "__main__":
    md_file = r"C:\Users\i\.gemini\antigravity-ide\brain\1c1b79f1-6a8b-41c4-84f5-e41d47015ef2\implementation_plan.md"
    pdf_file = r"y:\CLIENTE\nassara\buscador\plano_de_implementacao.pdf"
    create_pdf(md_file, pdf_file)
