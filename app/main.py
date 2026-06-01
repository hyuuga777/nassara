import os
import sys
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import (
    get_db, People, Sources, Events, Awards, Courses,
    Videos, News, SocialPosts, Students, Testimonials, MediaMentions,
    Timeline, Attachments, SearchParameters, SectionSummaries
)
from app.schemas import RelevanceMap, TimelineItem, Student, Testimonial, Source, Course, Event, News as NewsSchema, Video

app = FastAPI(
    title="Buscador Biográfico Inteligente - API",
    description="Backend API de alta performance para o memorial digital e linha do tempo profissional da Dra. Nássara Mesquita.",
    version="1.0.0"
)

# Configure CORS to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for local/development use
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    from app.database import SessionLocal, SearchParameters
    db = SessionLocal()
    try:
        count = db.query(SearchParameters).count()
        if count == 0:
            print("[Startup] Seeding default search parameters...")
            keywords = [
                {"value": "Nássara Mesquita", "label": "Nome principal", "notes": "Variação mais comum nas buscas"},
                {"value": "Nássara Borges Mesquita Oliveira", "label": "Nome completo", "notes": "Conforme registrado no Currículo Lattes"},
                {"value": "OLIVEIRA, N. B. M.", "label": "Citação bibliográfica", "notes": "Formato de citação em produções científicas"},
                {"value": "Dra. Nássara Mesquita", "label": "Nome profissional", "notes": "Formato usado em mídias e palestras"},
                {"value": "Nassara Mesquita Microtox", "label": "Técnica Microtox", "notes": "Associação de marca/técnica profissional"},
                {"value": "Nassara Mesquita harmonização facial", "label": "Especialidade principal", "notes": "Foco de atuação clínica"},
                {"value": "Mipps + HRF Facial Trainning", "label": "Curso internacional", "notes": "Curso de anatomia aplicada facial nos EUA"},
                {"value": "Summer Peel", "label": "Método estético", "notes": "Método de peeling químico e revitalização"},
                {"value": "Striort", "label": "Tratamento ortomolecular", "notes": "Técnica ortomolecular de combate a estrias"},
                {"value": "Flaci 10", "label": "Protocolo de flacidez", "notes": "Técnica Flaci 10 de tratamento corporal"},
                {"value": "Lipoescultura Gessada", "label": "Técnica corporal", "notes": "Tratamento ortomolecular para gordura localizada"}
            ]
            sites = [
                {"value": "lattes.cnpq.br/7120531705115048", "label": "Currículo Lattes", "notes": "Perfil oficial do CNPq"},
                {"value": "instagram.com/nassaramesquita", "label": "Instagram Oficial", "notes": "Principal canal de engajamento"},
                {"value": "escavador.com", "label": "Escavador", "notes": "Indexador acadêmico público"},
                {"value": "crfgo.org.br", "label": "CRF-GO", "notes": "Conselho Regional de Farmácia de Goiás"},
                {"value": "revistas.unilus.edu.br", "label": "Revista UNILUS", "notes": "Periódico do artigo de Fototerapia publicado em 2019"},
                {"value": "iepg.edu.br", "label": "IEPG", "notes": "Instituto de pós-graduação onde é coordenadora"},
                {"value": "cff.org.br", "label": "CFF", "notes": "Conselho Federal de Farmácia - GT Estética"},
                {"value": "faculdadecathedral.edu.br", "label": "Faculdades Cathedral", "notes": "Instituição onde orientou 17 monografias"}
            ]
            engines = [
                {"value": "Google Search", "label": "Google", "notes": "Principal motor de busca global"},
                {"value": "Google Scholar", "label": "Google Acadêmico", "notes": "Pesquisa de publicações e citações científicas"},
                {"value": "YouTube Search", "label": "YouTube", "notes": "Pesquisa de vídeos e podcasts"},
                {"value": "Bing", "label": "Bing", "notes": "Motor de busca secundário"}
            ]
            socials = [
                {"value": "instagram.com/dranassaramesquita", "label": "Instagram Profissional", "notes": "Perfil oficial da Dra. Nássara Mesquita no Instagram"},
                {"value": "facebook.com/dranassaramesquita", "label": "Facebook Profissional", "notes": "Perfil no Facebook"},
                {"value": "linkedin.com/in/nassara-mesquita-878880182", "label": "LinkedIn Acadêmico", "notes": "Perfil acadêmico e profissional no LinkedIn"}
            ]
            for kw in keywords:
                db.add(SearchParameters(type="keyword", value=kw["value"], label=kw["label"], notes=kw["notes"], active=1))
            for st in sites:
                db.add(SearchParameters(type="site", value=st["value"], label=st["label"], notes=st["notes"], active=1))
            for eg in engines:
                db.add(SearchParameters(type="engine", value=eg["value"], label=eg["label"], notes=eg["notes"], active=1 if eg["value"] != "Bing" else 0))
            for sc in socials:
                db.add(SearchParameters(type="social", value=sc["value"], label=sc["label"], notes=sc["notes"], active=1))
            db.commit()
            print("[Startup] Default search parameters seeded.")
    except Exception as e:
        print(f"[Startup] Error seeding default search parameters: {e}")
    finally:
        db.close()

# ── API Endpoints ─────────────────────────────────────────────────────────

@app.get("/api/profile")
def get_profile(db: Session = Depends(get_db)):
    profile = db.query(People).filter(People.name == "Dra. Nassara Mesquita").first()
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil profissional não localizado.")
    return {
        "name": profile.name,
        "bio": profile.bio,
        "birth_date": profile.birth_date,
        "status": profile.status,
        "registry_date": profile.registry_date,
        "metadata_json": profile.metadata_json
    }

@app.get("/api/timeline", response_model=List[TimelineItem])
def get_timeline(
    year: Optional[int] = None,
    month: Optional[int] = None,
    country_id: Optional[int] = None,
    state_id: Optional[int] = None,
    city_id: Optional[int] = None,
    institution_id: Optional[int] = None,
    university_id: Optional[int] = None,
    type: Optional[str] = None,
    category: Optional[str] = None,
    source_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Timeline)
    if year is not None:
        query = query.filter(Timeline.year == year)
    if month is not None:
        query = query.filter(Timeline.month == month)
    if country_id is not None:
        query = query.filter(Timeline.country_id == country_id)
    if state_id is not None:
        query = query.filter(Timeline.state_id == state_id)
    if city_id is not None:
        query = query.filter(Timeline.city_id == city_id)
    if institution_id is not None:
        query = query.filter(Timeline.institution_id == institution_id)
    if university_id is not None:
        query = query.filter(Timeline.university_id == university_id)
    if type is not None:
        query = query.filter(Timeline.type == type)
    if category is not None:
        query = query.filter(Timeline.category == category)
    if source_id is not None:
        query = query.filter(Timeline.source_id == source_id)
    
    # Sort chronologically by year (descending) and month (descending)
    return query.order_by(Timeline.year.desc(), Timeline.month.desc()).all()

@app.get("/api/relevance", response_model=RelevanceMap)
def get_relevance(db: Session = Depends(get_db)):
    """
    Calculate dynamic relevance mapping and metrics based on actual database counts.
    """
    # Count occurrences across all relational tables
    courses_count = db.query(Courses).count()
    events_count = db.query(Events).count()
    news_count = db.query(News).count()
    videos_count = db.query(Videos).count()
    students_count = db.query(Students).count()
    testimonials_count = db.query(Testimonials).count()
    mentions_count = db.query(MediaMentions).count()
    posts_count = db.query(SocialPosts).count()
    timeline_count = db.query(Timeline).count()
    
    # Calculate a weighted score representing public presence index
    appearances_score = (
        (courses_count * 15) + 
        (events_count * 10) + 
        (news_count * 8) + 
        (videos_count * 8) + 
        (posts_count * 4) + 
        (mentions_count * 12)
    )
    
    return RelevanceMap(
        total_courses=courses_count,
        total_events=events_count,
        total_news=news_count,
        total_videos=videos_count,
        total_students=students_count,
        total_testimonials=testimonials_count,
        total_media_mentions=mentions_count,
        total_social_posts=posts_count,
        total_timeline_items=timeline_count,
        total_appearances=appearances_score
    )

@app.get("/api/testimonials", response_model=List[Testimonial])
def get_testimonials(db: Session = Depends(get_db)):
    return db.query(Testimonials).all()

@app.get("/api/students", response_model=List[Student])
def get_students(db: Session = Depends(get_db)):
    return db.query(Students).all()

@app.get("/api/sources", response_model=List[Source])
def get_sources(db: Session = Depends(get_db)):
    return db.query(Sources).all()

@app.get("/api/courses", response_model=List[Course])
def get_courses(db: Session = Depends(get_db)):
    return db.query(Courses).all()

@app.get("/api/events", response_model=List[Event])
def get_events(db: Session = Depends(get_db)):
    return db.query(Events).all()

@app.get("/api/news", response_model=List[NewsSchema])
def get_news(db: Session = Depends(get_db)):
    return db.query(News).all()

@app.get("/api/videos", response_model=List[Video])
def get_videos(db: Session = Depends(get_db)):
    return db.query(Videos).all()

@app.get("/api/lattes")
def get_lattes_curriculum(db: Session = Depends(get_db)):
    """
    Generate grouped Lattes curriculum structures from enriched timeline records.
    """
    items = db.query(Timeline).order_by(Timeline.year.desc(), Timeline.month.desc()).all()
    
    curriculum = {
        "formacao": [],
        "atuacao": [],
        "producoes": [],
        "eventos": [],
        "cursos": [],
        "orientacoes": [],
        "certificacoes": []
    }
    
    for item in items:
        cat = (item.category or "").lower().strip()
        
        # Group chronologically into the 7 standard Lattes sections
        if "formacao" in cat or "graduação" in cat or "pós-graduação" in cat or "formação" in cat:
            section = "formacao"
        elif "atuacao" in cat or "atuação" in cat:
            section = "atuacao"
        elif "producoes" in cat or "produção" in cat or "produções" in cat or item.type == "video":
            section = "producoes"
        elif "eventos" in cat or "evento" in cat:
            section = "eventos"
        elif "cursos" in cat or "curso" in cat:
            section = "cursos"
        elif "orientacoes" in cat or "orientações" in cat or "mentoria" in cat:
            section = "orientacoes"
        elif "certificacoes" in cat or "certificações" in cat or item.type == "award":
            section = "certificacoes"
        else:
            # Fallback based on item type
            type_map = {
                "course": "cursos",
                "event": "eventos",
                "award": "certificacoes",
                "video": "producoes",
                "news": "producoes",
                "social": "producoes"
            }
            section = type_map.get(item.type, "atuacao")
            
        curriculum[section].append({
            "id": item.id,
            "year": item.year,
            "month": item.month,
            "type": item.type,
            "title": item.title,
            "description": item.description,
            "date": item.date,
            "participation_type": item.participation_type,
            "institution": item.institution.name if item.institution else None,
            "university": item.university.name if item.university else None,
            "location": f"{item.city.name}/{item.state.code}" if (item.city and item.state) else None
        })
        
    return curriculum

# ── Search Parameters CRUD ────────────────────────────────────────────────

@app.get("/api/search-params")
def get_search_params(db: Session = Depends(get_db)):
    """Return all search parameters grouped by type."""
    params = db.query(SearchParameters).order_by(SearchParameters.type, SearchParameters.id).all()
    result = {"keywords": [], "sites": [], "engines": [], "socials": []}
    type_map = {"keyword": "keywords", "site": "sites", "engine": "engines", "social": "socials"}
    for p in params:
        key = type_map.get(p.type, "keywords")
        result[key].append({
            "id": p.id,
            "type": p.type,
            "value": p.value,
            "label": p.label,
            "active": bool(p.active),
            "notes": p.notes,
            "created_at": p.created_at.isoformat() if p.created_at else None
        })
    return result

@app.post("/api/search-params")
def create_search_param(
    type: str,
    value: str,
    label: str = None,
    notes: str = None,
    db: Session = Depends(get_db)
):
    """Create a new search parameter."""
    from datetime import datetime
    param = SearchParameters(
        type=type,
        value=value,
        label=label or value,
        active=1,
        notes=notes,
        created_at=datetime.utcnow()
    )
    db.add(param)
    db.commit()
    db.refresh(param)
    return {"id": param.id, "type": param.type, "value": param.value, "label": param.label, "active": True}

@app.put("/api/search-params/{param_id}")
def update_search_param(
    param_id: int,
    value: str = None,
    label: str = None,
    active: int = None,
    notes: str = None,
    db: Session = Depends(get_db)
):
    """Update an existing search parameter."""
    param = db.query(SearchParameters).filter(SearchParameters.id == param_id).first()
    if not param:
        raise HTTPException(status_code=404, detail="Par\u00e2metro n\u00e3o encontrado.")
    if value is not None: param.value = value
    if label is not None: param.label = label
    if active is not None: param.active = active
    if notes is not None: param.notes = notes
    db.commit()
    return {"id": param.id, "type": param.type, "value": param.value, "active": bool(param.active)}

@app.delete("/api/search-params/{param_id}")
def delete_search_param(param_id: int, db: Session = Depends(get_db)):
    """Delete a search parameter."""
    param = db.query(SearchParameters).filter(SearchParameters.id == param_id).first()
    if not param:
        raise HTTPException(status_code=404, detail="Par\u00e2metro n\u00e3o encontrado.")
    db.delete(param)
    db.commit()
    return {"deleted": param_id}

@app.put("/api/timeline/{item_id}")
def update_timeline_item(
    item_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    date: Optional[str] = None,
    participation_type: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    item = db.query(Timeline).filter(Timeline.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item da linha do tempo não encontrado.")
    
    if title is not None: item.title = title
    if description is not None: item.description = description
    if year is not None: item.year = year
    if month is not None: item.month = month
    if date is not None: item.date = date
    if participation_type is not None: item.participation_type = participation_type
    if category is not None: item.category = category
    
    # Sync with children tables
    if item.source_table and item.source_row_id:
        table_name = item.source_table.lower()
        row_id = item.source_row_id
        if table_name == "courses":
            child = db.query(Courses).filter(Courses.id == row_id).first()
            if child:
                if title is not None: child.title = title
                if description is not None: child.description = description
                if date is not None: child.date = date
        elif table_name == "events":
            child = db.query(Events).filter(Events.id == row_id).first()
            if child:
                if title is not None: child.name = title
                if description is not None: child.description = description
                if date is not None: child.date = date
        elif table_name == "videos":
            child = db.query(Videos).filter(Videos.id == row_id).first()
            if child:
                if title is not None: child.title = title
                if description is not None: child.summary = description
                if date is not None: child.date = date
        elif table_name == "news":
            child = db.query(News).filter(News.id == row_id).first()
            if child:
                if title is not None: child.title = title
                if description is not None: child.summary = description
                if date is not None: child.date = date
        elif table_name == "awards":
            child = db.query(Awards).filter(Awards.id == row_id).first()
            if child:
                if title is not None: child.title = title
                if description is not None: child.description = description
                if date is not None: child.date = date
        elif table_name == "socials" or table_name == "socialposts":
            child = db.query(SocialPosts).filter(SocialPosts.id == row_id).first()
            if child:
                if description is not None: child.content = description
                if date is not None: child.date = date

    db.commit()
    return {"status": "success", "message": "Item atualizado com sucesso", "id": item.id}

@app.get("/api/section-summaries/{section_name}")
def get_section_summary(section_name: str, db: Session = Depends(get_db)):
    summary = db.query(SectionSummaries).filter(SectionSummaries.section_name == section_name).first()
    if not summary:
        return {"section_name": section_name, "content": ""}
    return {"section_name": summary.section_name, "content": summary.content, "updated_at": summary.updated_at}

@app.put("/api/section-summaries/{section_name}")
def update_section_summary(section_name: str, content: str, db: Session = Depends(get_db)):
    summary = db.query(SectionSummaries).filter(SectionSummaries.section_name == section_name).first()
    if not summary:
        summary = SectionSummaries(section_name=section_name, content=content)
        db.add(summary)
    else:
        summary.content = content
    db.commit()
    db.refresh(summary)
    return {"status": "success", "content": summary.content}

@app.post("/api/section-summaries/{section_name}/generate")
def generate_section_summary(section_name: str, db: Session = Depends(get_db)):
    context_texts = []
    if section_name == "courses":
        items = db.query(Courses).all()
        for idx, it in enumerate(items):
            context_texts.append(f"Curso {idx+1}: {it.title} - Data: {it.date} - Função: {'Instrutora/Professora' if it.role == 'instructor' else 'Aluna'} - {it.description or ''}")
    elif section_name == "events":
        items = db.query(Events).all()
        for idx, it in enumerate(items):
            context_texts.append(f"Evento {idx+1}: {it.name} - Data: {it.date} - Local: {it.location} - {it.description or ''}")
    elif section_name == "videos":
        items = db.query(Videos).all()
        for idx, it in enumerate(items):
            context_texts.append(f"Vídeo/Podcast {idx+1}: {it.title} - Resumo: {it.summary or ''}")
    elif section_name == "news":
        items = db.query(News).all()
        for idx, it in enumerate(items):
            context_texts.append(f"Notícia/Imprensa {idx+1}: {it.title} - Editora: {it.publisher} - Data: {it.date} - Resumo: {it.summary or ''}")
    elif section_name == "testimonials":
        items = db.query(Testimonials).all()
        for idx, it in enumerate(items):
            context_texts.append(f"Depoimento {idx+1} por {it.author} ({it.relation or 'Aluno'}): \"{it.content}\"")
        students = db.query(Students).all()
        student_names = [s.name for s in students]
        if student_names:
            context_texts.append(f"Lista de alunos mentorados/orientados: {', '.join(student_names)}")
    else:
        raise HTTPException(status_code=400, detail="Seção inválida para geração de resumo.")

    context_str = "\n".join(context_texts)
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    generated_content = ""
    
    if gemini_key:
        try:
            import httpx
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            headers = {"Content-Type": "application/json"}
            prompt = (
                f"Você é um redator biográfico profissional para a Dra. Nássara Mesquita (Farmacêutica Esteta, especialista em Microtox, Toxina Botulínica e Harmonização Facial de alta performance em Goiânia/GO).\n"
                f"Com base nas informações abaixo cadastradas na seção de '{section_name.upper()}', crie um texto 'Sobre' resumido e super atrativo de 2 a 4 frases que apresente o impacto e a relevância profissional dela nessa área.\n"
                f"Regras:\n"
                f"- O texto deve ser escrito em terceira pessoa do singular, tom premium, elegante, objetivo e profissional.\n"
                f"- Destaque os números relevantes (como a quantidade de alunos, diversidade de locais, parcerias como a Delta Proto, ou a autoridade das palestras e premiações).\n"
                f"- Retorne APENAS o texto final do resumo, sem introduções, aspas extras ou explicações.\n\n"
                f"DADOS DA SEÇÃO:\n{context_str}"
            )
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 250
                }
            }
            response = httpx.post(url, headers=headers, json=payload, timeout=10.0)
            if response.status_code == 200:
                resp_json = response.json()
                generated_content = resp_json['candidates'][0]['content']['parts'][0]['text'].strip()
        except Exception as e:
            print(f"[Gemini API Exception] {e}. Falling back to heuristic generator.")
            
    if not generated_content:
        # Heuristic/Rule-based Fallback Generator of High Quality
        if section_name == "courses":
            generated_content = (
                f"A Dra. Nássara Mesquita possui uma sólida trajetória de liderança e docência na área de saúde estética, "
                f"tendo ministrado e participado de {len(db.query(Courses).all())} importantes cursos e mentorias profissionais "
                f"de alto nível. É amplamente reconhecida como referência nacional e pioneira clínica pelo desenvolvimento do inovador método Microtox "
                f"e suas mentorias personalizadas de alta performance em Goiânia e diversas capitais."
            )
        elif section_name == "events":
            generated_content = (
                f"Como palestrante de destaque nacional, a Dra. Nássara Mesquita atua ativamente em congressos científicos, "
                f"seminários e simpósios em todo o Brasil. Sua presença constante em fóruns como o XII Congresso Mundial de Farmacêuticos "
                f"e comissões reguladoras do CRF e CFF consolida sua autoridade clínica de ponta frente à farmácia estética."
            )
        elif section_name == "videos":
            generated_content = (
                f"A difusão do conhecimento estético e a educação profissional fazem parte da essência biográfica da Dra. Nássara Mesquita. "
                f"Através de entrevistas de alta visibilidade nacional (como na TV Caras / IBTV), podcasts de anatomia facial aplicada e reels com execução passo a passo "
                f"de protocolos práticos, ela educa milhares de profissionais com base em biossegurança e resultados refinados."
            )
        elif section_name == "news":
            generated_content = (
                f"Com forte destaque na mídia especializada e conselhos de classe, a presença na imprensa da Dra. Nássara Mesquita "
                f"valida a excelência de suas técnicas inovadoras. Suas publicações e entrevistas científicas na Revista do CRF abordam "
                f"a regulamentação profissional, tratamentos regenerativos modernos e a segurança dermoestética com respaldo ético indiscutível."
            )
        elif section_name == "testimonials":
            students_count = db.query(Students).count()
            generated_content = (
                f"Completando uma expressiva marca acadêmica, a Dra. Nássara Mesquita já orientou e supervisionou formalmente "
                f"mais de {students_count} monografias e teses científicas de especialização em Saúde Estética e Cosmetologia. "
                f"O carinho e a profunda gratidão de centenas de alunos mentorados e pacientes fiéis atestam sua maestria clínica, "
                f"ética impecável e grande dedicação ao ensino."
            )

    # Save to database
    summary = db.query(SectionSummaries).filter(SectionSummaries.section_name == section_name).first()
    if not summary:
        summary = SectionSummaries(section_name=section_name, content=generated_content)
        db.add(summary)
    else:
        summary.content = generated_content
    db.commit()
    db.refresh(summary)
    return {"status": "success", "content": summary.content}

# Root landing check
@app.get("/")
def read_root():
    return {
        "status": "online",
        "app": "Buscador Biogr\u00e1fico Inteligente - Dra. N\u00e1ssara Mesquita",
        "version": "1.0.0",
        "endpoints": {
            "profile": "/api/profile",
            "timeline": "/api/timeline",
            "relevance": "/api/relevance",
            "testimonials": "/api/testimonials",
            "students": "/api/students",
            "sources": "/api/sources",
            "courses": "/api/courses",
            "events": "/api/events",
            "news": "/api/news",
            "videos": "/api/videos",
            "search_params": "/api/search-params"
        }
    }
