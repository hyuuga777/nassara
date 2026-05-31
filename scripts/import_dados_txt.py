"""
Script de importação de dados do arquivo dados.txt para o banco de dados.
Extrai: formação complementar, participação em eventos, produções, orientações e prêmios do Lattes.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, Sources, Courses, Events, Timeline, Awards, Students, get_db, init_db
from datetime import datetime

db = SessionLocal()

# ── Fonte: Lattes CNPq ──────────────────────────────────────────────────────
lattes_source = db.query(Sources).filter(Sources.url == "https://lattes.cnpq.br/7120531705115048").first()
if not lattes_source:
    lattes_source = Sources(
        title="Currículo Lattes - Nássara Borges Mesquita Oliveira",
        url="https://lattes.cnpq.br/7120531705115048",
        type="lattes",
        capture_date=datetime(2026, 5, 31),
        metadata_json='{"lattes_id": "7120531705115048", "last_update": "31/05/2026"}'
    )
    db.add(lattes_source)
    db.commit()
    db.refresh(lattes_source)
    print(f"[+] Fonte Lattes criada: {lattes_source.id}")
else:
    print(f"[=] Fonte Lattes já existe: {lattes_source.id}")

escavador_source = db.query(Sources).filter(Sources.url == "https://www.escavador.com/sobre/1048461/nassara-borges-mesquita-oliveira").first()
if not escavador_source:
    escavador_source = Sources(
        title="Escavador - Nássara Borges Mesquita Oliveira",
        url="https://www.escavador.com/sobre/1048461/nassara-borges-mesquita-oliveira",
        type="escavador",
        capture_date=datetime(2026, 5, 31),
    )
    db.add(escavador_source)
    db.commit()
    db.refresh(escavador_source)

# ── Helper: upsert timeline item ─────────────────────────────────────────────
def add_timeline(year, month, type_, title, description, category, participation_type=None, source_id=None):
    exists = db.query(Timeline).filter(
        Timeline.year == year,
        Timeline.title == title,
        Timeline.type == type_
    ).first()
    if not exists:
        item = Timeline(
            year=year,
            month=month,
            type=type_,
            title=title,
            description=description,
            category=category,
            participation_type=participation_type,
            source_id=source_id,
            date=f"{month:02d}/{year}" if month else str(year),
        )
        db.add(item)
        db.commit()
        print(f"  [+] Timeline: {year} - {title[:60]}")
    else:
        print(f"  [=] Já existe: {year} - {title[:60]}")

# ── Helper: upsert course ─────────────────────────────────────────────────────
def add_course(title, date, role, description, source_id):
    exists = db.query(Courses).filter(Courses.title == title, Courses.date == date).first()
    if not exists:
        c = Courses(title=title, date=date, role=role, description=description, source_id=source_id)
        db.add(c)
        db.commit()
        print(f"  [+] Curso: {date} - {title[:60]}")
    else:
        print(f"  [=] Curso já existe: {title[:60]}")

# ── Helper: upsert event ──────────────────────────────────────────────────────
def add_event(name, date, description, source_id, location=None):
    exists = db.query(Events).filter(Events.name == name).first()
    if not exists:
        e = Events(name=name, date=date, description=description, source_id=source_id, location=location)
        db.add(e)
        db.commit()
        print(f"  [+] Evento: {date} - {name[:60]}")

# ── Helper: upsert award ──────────────────────────────────────────────────────
def add_award(title, date, institution, description, source_id):
    exists = db.query(Awards).filter(Awards.title == title).first()
    if not exists:
        a = Awards(title=title, date=date, institution=institution, description=description, source_id=source_id)
        db.add(a)
        db.commit()
        print(f"  [+] Prêmio: {date} - {title[:60]}")

# ── Helper: upsert student/orientation ───────────────────────────────────────
def add_student(name, source_id, testimonial=None):
    exists = db.query(Students).filter(Students.name == name).first()
    if not exists:
        s = Students(name=name, source_id=source_id, testimonial=testimonial, date="2018")
        db.add(s)
        db.commit()
        print(f"  [+] Orientando: {name}")

# ═══════════════════════════════════════════════════════════════════
# FORMAÇÃO COMPLEMENTAR (Cursos realizados - role=student)
# ═══════════════════════════════════════════════════════════════════
print("\n[PIPELINE] Importando formação complementar...")

cursos_realizados = [
    ("2019", "Mipps + HRF Facial Trainning (IAA - EUA)", "Treinamento intensivo de 24h em técnicas avançadas de aplicação facial no Institute Off Applied Anatomy, EUA.", "student"),
    ("2019", "O Futuro da Estética Aliada à Inteligência Artificial (CUHK - Hong Kong)", "Curso de 40h na The Chinese University of Hong Kong sobre IA aplicada à personalização estética.", "student"),
    ("2018", "Peeling de Fenol Light (PERFECTOUS - Brasil)", "Curso de 8h em Biomedicina Estética e Laser pela PERFECTOUS.", "student"),
    ("2018", "Programa Afine-se de Qualidade de Vida e Emagrecimento (AFINE-SE)", "Programa de 30h em emagrecimento inteligente.", "student"),
    ("2017", "Flaci 10 - Conceito FLACI10 (Brasil)", "Técnica Flaci 10, 8h de capacitação.", "student"),
    ("2016", "Preenchimento Facial e Fios de Sustentação (IBOP - Brasil)", "Curso de 24h pelo Instituto Brasileiro de Odontologia Preventiva.", "student"),
    ("2016", "Capacitação do Método Summer Peel (SP - Brasil)", "Método Summer Peel, 20h de treinamento.", "student"),
    ("2016", "Lipoescultura Gessada (Bothanica Mineral - Brasil)", "Técnica de 8h pela Bothanica Mineral.", "student"),
    ("2016", "Técnica Ortomolecular de Combate a Estrias (STRIORT - Brasil)", "Capacitação em técnica ortomolecular.", "student"),
    ("2015", "Técnica de Microagulhamento, Radiofrequência e Cosmetologia Avançada (LB - Brasil)", "8h com Ludmila Bonelli Cosmética Avançada.", "student"),
    ("2013", "Dermaroiler, Peelings Químicos e Intradermoterapia (ASGARD)", "Curso de 4h pela ASGARD.", "student"),
    ("2011", "Capacitação sobre Legislação Farmacêutica (CRF-GO)", "8h pelo Conselho Regional de Farmácia de Goiás.", "student"),
    ("2011", "Curso Básico de Oncologia (ACCG - Brasil)", "28h pelo Instituto de Ensino e Pesquisa da Associação de Combate ao Câncer.", "student"),
    ("2009", "Curso de Injetáveis com Segurança (UFG - Goiânia)", "12h pela Universidade Federal de Goiás.", "student"),
    ("2009", "Curso de Métodos Contraceptivos (UNIP)", "3h pela Universidade Paulista.", "student"),
    ("2006", "Extensão Comunitária de Redação e Expressão (UNIP)", "4h pela Universidade Paulista.", "student"),
    ("2006", "Extensão Comunitária de Matemática Financeira (UNIP)", "3h pela Universidade Paulista.", "student"),
]

for year, title, desc, role in cursos_realizados:
    add_course(title, year, role, desc, lattes_source.id)
    yr = int(year)
    cat = "Cursos" if role == "instructor" else "Formação Complementar"
    add_timeline(yr, None, "course", title, desc, cat, "Realizou" if role == "student" else "Ministrou", lattes_source.id)

# ═══════════════════════════════════════════════════════════════════
# PARTICIPAÇÃO EM EVENTOS (Congressos, Palestras, Seminários)
# ═══════════════════════════════════════════════════════════════════
print("\n[PIPELINE] Importando participação em eventos...")

eventos = [
    ("2018", "2º Congresso Pan-Amazônico de Ciências Farmacêuticas", "Procedimentos Estéticos Avançados: novas tecnologias e métodos de aplicação. Atuou como Moderador.", "Moderador"),
    ("2016", "1º Encontro de Farmácia Estética do Tocantins", "A atuação do farmacêutico na estética, a rentabilidade do profissional capacitado e perspectivas do profissional na estética.", "Palestrante"),
    ("2016", "6º Congresso Norte e Nordeste de Ciências Farmacêuticas", "Cuidado Farmacêutico na Estética. Atuou como Moderador.", "Moderador"),
    ("2016", "I Workshop de Farmácia Estética", "Participação no I Workshop de Farmácia Estética.", "Palestrante"),
    ("2016", "IX Jornada Farmacêutica", "Estética: uma nova perspectiva para o profissional farmacêutico.", "Palestrante"),
    ("2016", "XII JAFARMA - Jornada Acadêmica de Farmácia", "Estética - Uma nova perspectiva para o profissional farmacêutico.", "Palestrante"),
    ("2015", "10º Congresso Regional de Análises Clínicas do Centro-Oeste", "Minicurso: Estética para Profissionais da Saúde - enfoque nos procedimentos injetáveis.", "Palestrante"),
    ("2015", "8º FarmaFlorence - Farmacêutico: do Medicamento às Práticas Integrativas", "O Farmacêutico na Saúde Estética.", "Palestrante"),
    ("2015", "CRF-GO - Assistência Farmacêutica no Diabetes", "Moderador no Congresso do Conselho Regional de Farmácia do Estado de Goiás.", "Moderador"),
    ("2011", "I Simpósio Multidisciplinar de Doenças Infecciosas e Parasitárias", "Participação no I Simpósio Multidisciplinar.", "Participante"),
    ("2009", "IV Jornada Acadêmica de Fisioterapia", "Participação na IV Jornada Acadêmica.", "Participante"),
    ("2009", "V JAFARMA e III Ciclo de Palestras de Biomedicina", "Participação no V JAFARMA.", "Participante"),
    ("2009", "VI JAFARMA e IV Ciclo de Palestras de Biomedicina", "Participação no VI JAFARMA.", "Participante"),
    ("2008", "XXXI ENEF – Encontro Nacional dos Estudantes de Farmácia", "Participação no Encontro Nacional.", "Participante"),
    ("2006", "II JAFARMA - Jornada Acadêmica de Farmácia da UNIP", "Participação no II JAFARMA.", "Participante"),
    ("2009", "Aula Inaugural do Programa de Pós Graduação de Educação da UCG", "Co-organização com Iria Brzezinski da Aula Inaugural do PPG Educação UCG.", "Organizador"),
]

for year, name, desc, participation in eventos:
    add_event(name, year, desc, lattes_source.id)
    yr = int(year)
    add_timeline(yr, None, "event", name, desc, "Eventos", participation, lattes_source.id)

# ═══════════════════════════════════════════════════════════════════
# PRODUÇÕES BIBLIOGRÁFICAS (Palestras e Apresentações)
# ═══════════════════════════════════════════════════════════════════
print("\n[PIPELINE] Importando produções bibliográficas...")

producoes = [
    ("2019", "Evolução da Fototerapia de Baixa Intensidade, seus Fotofármacos e o impacto sobre procedimentos estéticos", "Artigo publicado na Revista UNILUS Ensino e Pesquisa Online, v.16, p.143-151. Co-autoria com C.S. Santos, G.M.P. Santos, J.R.P.P. Fiuza et al.", "Artigo"),
    ("2018", "Humanização em Saúde: Desafios e os Novos Cenários", "Apresentação de palestra sobre humanização na saúde.", "Palestra"),
    ("2018", "Procedimentos Estéticos Avançados: novas tecnologias e métodos de aplicação", "Conferência sobre procedimentos estéticos e novas tecnologias.", "Palestra"),
    ("2017", "Atenção Farmacêutica na Saúde Estética", "Palestra sobre atenção farmacêutica aplicada à estética.", "Palestra"),
    ("2017", "Cuidados Farmacêuticos nas Disfunções Estéticas", "Palestra sobre cuidados farmacêuticos.", "Palestra"),
    ("2017", "Palestrante - Workshop Ser Farmacêutico na Estética", "Participação como palestrante no Workshop.", "Palestra"),
    ("2017", "Técnicas Estéticas eficientes aos tratamentos de emagrecimento e gordura localizada", "Co-autoria com H. Guerim em palestra sobre técnicas para emagrecimento.", "Palestra"),
    ("2017", "Cuidados e Serviços Farmacêuticos na Estética", "Curso de curta duração ministrado sobre cuidados farmacêuticos na estética.", "Curso"),
    ("2016", "A Evolução da Atuação do Farmacêutico na Estética", "Palestra sobre a evolução do papel do farmacêutico.", "Palestra"),
    ("2016", "Estética - Uma Nova Perspectiva para o Profissional Farmacêutico", "Palestra sobre novas perspectivas na farmácia estética.", "Palestra"),
    ("2016", "Intradermoterapia Aplicada às Disfunções Estéticas", "Palestra técnica sobre intradermoterapia.", "Palestra"),
    ("2016", "Saúde Estética: um mercado promissor", "Palestra sobre o mercado de saúde estética.", "Palestra"),
    ("2016", "Workshop de Farmácia Estética", "Palestra e workshop de farmácia estética.", "Palestra"),
    ("2015", "Disfunções Estéticas", "Apresentação em congresso sobre disfunções estéticas.", "Palestra"),
    ("2015", "O Farmacêutico Esteta, um Mercado Promissor", "Palestra sobre o mercado promissor para farmacêuticos.", "Palestra"),
    ("2015", "O Farmacêutico na Saúde Estética", "Palestra sobre a atuação do farmacêutico na saúde estética.", "Palestra"),
    ("2015", "Disfunção Estética (Curso Ministrado)", "Curso de curta duração ministrado sobre disfunção estética.", "Curso"),
    ("2015", "Limpeza de Pele (Curso Ministrado)", "Curso de curta duração ministrado sobre limpeza de pele.", "Curso"),
]

for year, title, desc, tipo in producoes:
    yr = int(year)
    cat = "Produções" if tipo in ("Artigo", "Palestra") else "Cursos"
    add_timeline(yr, None, "course" if tipo == "Curso" else "event", title, desc, cat, "Professora" if tipo == "Curso" else "Palestrante", lattes_source.id)

# ═══════════════════════════════════════════════════════════════════
# ORIENTAÇÕES (Monografias orientadas em 2018)
# ═══════════════════════════════════════════════════════════════════
print("\n[PIPELINE] Importando orientações de monografias...")

orientandos = [
    ("Sinara de Souza Cunha Fernandes", "Eficácia do microagulhamento associado à vitamina C: uma revisão"),
    ("Rafaele Fernando Soares Horman", "O Processo de Depilação a laser de diodo: uma análise comparativa"),
    ("Marcela Cristina Fonseca", "Mesoterapia em estética"),
    ("Lívia Ferreira de Sousa", "Peelings Químicos no Tratamento de Acne"),
    ("Lílian de Abreu Ferreira", "Microagulhamento no Tratamento de Cicatrizes Atróficas da Acne: revisão sistemática"),
    ("Cristhiany Salviano de Oliveira", "A Efetividade do Ultrassom no Tratamento da Fibro Edema Gelóide (FEG)"),
    ("Catarina Maciel Trindade", "Alopecia Areata: uma abordagem sobre antigos e novos tratamentos disponíveis"),
    ("Camilla Christine Marques", "Uso Estético e Aplicação de Toxina Botulínica: uma revisão de literatura"),
    ("Astréia Terezinha Gomes Hergl Magalhães", "As Controvérsias da Criolipólise: revisão da literatura"),
    ("Ana Paula Pires Pessoa", "Eficácia de Tretinoína e Associações de Tretinoína no Tratamento da Acne Vulgar"),
    ("Aline Gonçalves Coelho", "Tratamento Estético Injetável de Microvasos com Glicose 75% e Glicose 50%"),
    ("Paloma de Carvalho Bertoldo", "Benefícios do Microagulhamento na Cicatriz de Acne"),
    ("Lidiany Soares Viana Olevate", "Biossegurança em Estética"),
    ("Danielle Batista do Amaral de Borba", "Rejuvenecimento Facial Através da Indução do Colágeno Usando Microagulhamento"),
    ("Ana Mirna Lisboa Miranda", "Melhora na Aparência das Estrias Através do Microagulhamento"),
    ("Alice Pinto Coelho de Carvalho", "O Uso do Peeling de Ácido Salicílico no Tratamento de Acne"),
    ("Márcia Amélia Cardoso de Carvalho", "A Mesoterapia no Tratamento de Celulite"),
]

for name, work in orientandos:
    add_student(name, lattes_source.id, f"Monografia orientada: {work} (Faculdades Cathedral de Ensino Superior, 2018)")

add_timeline(2018, None, "course", "Orientação de 17 Monografias de Especialização em Saúde Estética e Cosmética",
    "Orientou 17 monografias de conclusão de especialização nas Faculdades Cathedral de Ensino Superior nas áreas de Microagulhamento, Peelings, Toxina Botulínica, Depilação a Laser, Mesoterapia, Criolipólise, entre outros.",
    "Orientações", "Orientadora", lattes_source.id)

# ═══════════════════════════════════════════════════════════════════
# PRÊMIOS
# ═══════════════════════════════════════════════════════════════════
print("\n[PIPELINE] Importando prêmios...")
add_award(
    "Honra ao Mérito - Sessão Especial em Homenagem ao CRF e Sindicato dos Farmacêuticos",
    "2016",
    "Câmara Municipal de Goiânia",
    "Reconhecimento honorífico pela Câmara Municipal de Goiânia em sessão especial em homenagem ao Conselho Regional de Farmácia e ao Sindicato dos Farmacêuticos.",
    lattes_source.id
)
add_timeline(2016, None, "award", "Honra ao Mérito - Câmara Municipal de Goiânia",
    "Reconhecimento honorífico pela Câmara Municipal de Goiânia em sessão especial em homenagem ao CRF-GO e Sindicato dos Farmacêuticos.",
    "Prêmios", "Homenageada", lattes_source.id)

# ═══════════════════════════════════════════════════════════════════
# FORMAÇÃO ACADÊMICA Principal (garantir existência)
# ═══════════════════════════════════════════════════════════════════
print("\n[PIPELINE] Verificando formação acadêmica principal...")
formacoes = [
    (2013, 7, "course", "Especialização em Saúde Estética (Faculdade Arthur Thomas - FAAT, Londrina)", "Especialização em Saúde Estética concluída em 2013 pela Faculdade Arthur Thomas, Londrina, Brasil.", "Formação Acadêmica", "Estudante"),
    (2012, 12, "course", "Especialização em Hematologia Clínica e Banco de Sangue (FAT)", "Especialização em Hematologia Clínica e Banco de Sangue pela Faculdade Arthur Thomas.", "Formação Acadêmica", "Estudante"),
    (2011, 12, "course", "Graduação em Farmácia-Bioquímica (UNIP - Universidade Paulista)", "Graduação em Farmácia-Bioquímica pela Universidade Paulista, concluída em 2011.", "Formação Acadêmica", "Graduada"),
]

for year, month, type_, title, desc, cat, partic in formacoes:
    add_timeline(year, month, type_, title, desc, cat, partic, lattes_source.id)

db.close()
print("\n[PIPELINE] ✅ Importação concluída com sucesso!")
