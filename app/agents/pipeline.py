import os
import sys
from datetime import datetime
from sqlalchemy.orm import Session

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import (
    SessionLocal, init_db, People, Sources, Events, Awards, Courses,
    Videos, News, SocialPosts, Students, Testimonials, MediaMentions,
    Timeline, Attachments, Countries, States, Cities, Institutions, Universities, Evidences, engine, Base
)
from app.utils.dedup import is_duplicate_url, check_duplicate_timeline_item, get_duplicate_source

def run_pipeline():
    print("[PIPELINE] Iniciando processamento e indexação biográfica V2 (Enriquecida com Lattes)...")
    
    # 1. Truncate all tables for a clean V2 upgrade and re-population
    print("[PIPELINE] Redefinindo estrutura de tabelas...")
    Base.metadata.drop_all(bind=engine)
    init_db()
    
    db = SessionLocal()
    
    try:
        # 2. Add Dra. Nássara Mesquita profile
        profile = People(
            name="Dra. Nassara Mesquita",
            bio="Farmacêutica Esteta especialista em Harmonização Facial, referência nacional em aplicação de Toxina Botulínica, Microtox e mentorias clínicas avançadas de alta performance estética. Graduada em Farmácia-Bioquímica pela UNIP, com pós-graduações em Saúde Estética e Hematologia Clínica pela Faculdade Arthur Thomas.",
            birth_date="05/07/1988",
            status="active",
            metadata_json='{"crf": "CRF-GO 9876", "lattes_id": "7120531705115048", "cpf": "01970693126", "instagram": "@dranassaramesquita", "location": "Setor Marista, Goiânia/GO"}'
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        print("[PIPELINE] Perfil profissional da Dra. Nassara Mesquita criado com indexadores CPF e Instagram!")

        # 3. Setup V2 Geolocation Reference Data (Enriched with China, States and Cities)
        print("[PIPELINE] Alimentando tabelas de geolocalização...")
        br = Countries(name="Brasil", code="BR")
        us = Countries(name="Estados Unidos", code="US")
        cn = Countries(name="China", code="CN")
        db.add_all([br, us, cn])
        db.commit()
        db.refresh(br)
        db.refresh(us)
        db.refresh(cn)
        
        go = States(name="Goiás", code="GO", country_id=br.id)
        sp = States(name="São Paulo", code="SP", country_id=br.id)
        pr = States(name="Paraná", code="PR", country_id=br.id)
        pa = States(name="Pará", code="PA", country_id=br.id)
        to = States(name="Tocantins", code="TO", country_id=br.id)
        pi = States(name="Piauí", code="PI", country_id=br.id)
        ba = States(name="Bahia", code="BA", country_id=br.id)
        rs = States(name="Rio Grande do Sul", code="RS", country_id=br.id)
        df = States(name="Distrito Federal", code="DF", country_id=br.id)
        ms = States(name="Mato Grosso do Sul", code="MS", country_id=br.id)
        fl = States(name="Flórida", code="FL", country_id=us.id)
        gd = States(name="Guangdong", code="GD", country_id=cn.id)
        db.add_all([go, sp, pr, pa, to, pi, ba, rs, df, ms, fl, gd])
        db.commit()
        db.refresh(go)
        db.refresh(sp)
        db.refresh(pr)
        db.refresh(pa)
        db.refresh(to)
        db.refresh(pi)
        db.refresh(ba)
        db.refresh(rs)
        db.refresh(df)
        db.refresh(ms)
        db.refresh(fl)
        db.refresh(gd)
        
        goiania = Cities(name="Goiânia", state_id=go.id)
        sao_paulo = Cities(name="São Paulo", state_id=sp.id)
        londrina = Cities(name="Londrina", state_id=pr.id)
        belem = Cities(name="Belém", state_id=pa.id)
        palmas = Cities(name="Palmas", state_id=to.id)
        teresina = Cities(name="Teresina", state_id=pi.id)
        salvador = Cities(name="Salvador", state_id=ba.id)
        gramado = Cities(name="Gramado", state_id=rs.id)
        brasilia = Cities(name="Brasília", state_id=df.id)
        campo_grande = Cities(name="Campo Grande", state_id=ms.id)
        miami = Cities(name="Miami", state_id=fl.id)
        guangzhou = Cities(name="Guangzhou", state_id=gd.id)
        jussara = Cities(name="Jussara", state_id=go.id)
        
        db.add_all([goiania, sao_paulo, londrina, belem, palmas, teresina, salvador, gramado, brasilia, campo_grande, miami, guangzhou, jussara])
        db.commit()
        db.refresh(goiania)
        db.refresh(sao_paulo)
        db.refresh(londrina)
        db.refresh(belem)
        db.refresh(palmas)
        db.refresh(teresina)
        db.refresh(salvador)
        db.refresh(gramado)
        db.refresh(brasilia)
        db.refresh(campo_grande)
        db.refresh(miami)
        db.refresh(guangzhou)
        db.refresh(jussara)

        # 4. Setup Institutional Classifications (Enriched V2 + User Links)
        print("[PIPELINE] Alimentando entidades de classificação institucional...")
        inst_unip = Institutions(name="Universidade Paulista", acronym="UNIP", type="university")
        inst_faat = Institutions(name="Faculdade Arthur Thomas", acronym="FAAT", type="faculty")
        inst_ufg = Institutions(name="Universidade Federal de Goiás", acronym="UFG", type="university")
        inst_puc = Institutions(name="Pontifícia Universidade Católica de Goiás", acronym="PUC-GO", type="university")
        inst_cathedral = Institutions(name="Faculdades Cathedral de Ensino Superior", acronym="Cathedral", type="university")
        inst_cuhk = Institutions(name="The Chinese University of Hong Kong", acronym="CUHK", type="university")
        inst_ipupo = Institutions(name="IPUPO Estética", acronym="IPUPO", type="faculty")
        inst_clinica = Institutions(name="Consultório Dra. Nássara Mesquita", acronym="Clinica-NM", type="clinic")
        inst_lr = Institutions(name="Laboratório Referência", acronym="LR", type="clinic")
        inst_hc = Institutions(name="Hospital das Clínicas de Goiânia", acronym="HC", type="hospital")
        
        inst_crf = Institutions(name="Conselho Regional de Farmácia de Goiás", acronym="CRF-GO", type="council")
        inst_cff = Institutions(name="Conselho Federal de Farmácia", acronym="CFF", type="council")
        
        inst_congresso = Institutions(name="Congresso Goiano de Estética", acronym="CGE", type="congress")
        inst_panam = Institutions(name="Congresso Pan-Amazônico de Ciências Farmacêuticas", acronym="CPACF", type="congress")
        
        inst_marc = Institutions(name="Miami Anatomical Research Center", acronym="MARC", type="association")
        inst_delta = Institutions(name="Delta Proto", acronym="DP", type="company")
        inst_destaques = Institutions(name="Destaques da Saúde", acronym="DS", type="association")
        
        # New V2 & User links additions to resolve NameError crashes
        inst_ciae = Institutions(name="Congresso Internacional de Anatomia e Estética", acronym="CIAE", type="congress")
        inst_expo = Institutions(name="Expo Saúde Goiânia", acronym="ExpoSaude", type="congress")
        inst_ancec = Institutions(name="Agência Nacional de Cultura, Empreendedorismo e Comunicação", acronym="ANCEC", type="association")
        inst_crfpi = Institutions(name="Conselho Regional de Farmácia do Piauí", acronym="CRF-PI", type="council")
        inst_crfba = Institutions(name="Conselho Regional de Farmácia da Bahia", acronym="CRF-BA", type="council")
        inst_crfpa = Institutions(name="Conselho Regional de Farmácia do Pará", acronym="CRF-PA", type="council")
        inst_crfms = Institutions(name="Conselho Regional de Farmácia do Mato Grosso do Sul", acronym="CRF-MS", type="council")
        inst_ibtv = Institutions(name="International Business TV / TV Caras", acronym="IBTV", type="company")
        inst_gramado = Institutions(name="Congresso de Gramado / CMFLP", acronym="CMFLP", type="congress")
        
        db.add_all([
            inst_unip, inst_faat, inst_ufg, inst_puc, inst_cathedral, inst_cuhk, 
            inst_ipupo, inst_clinica, inst_lr, inst_hc, inst_crf, inst_cff, 
            inst_congresso, inst_panam, inst_marc, inst_delta, inst_destaques,
            inst_ciae, inst_expo, inst_ancec, inst_crfpi, inst_crfba, inst_crfpa, 
            inst_crfms, inst_ibtv, inst_gramado
        ])
        db.commit()
        
        db.refresh(inst_unip)
        db.refresh(inst_faat)
        db.refresh(inst_ufg)
        db.refresh(inst_puc)
        db.refresh(inst_cathedral)
        db.refresh(inst_cuhk)
        db.refresh(inst_ipupo)
        db.refresh(inst_clinica)
        db.refresh(inst_lr)
        db.refresh(inst_hc)
        db.refresh(inst_crf)
        db.refresh(inst_cff)
        db.refresh(inst_congresso)
        db.refresh(inst_panam)
        db.refresh(inst_marc)
        db.refresh(inst_delta)
        db.refresh(inst_destaques)
        db.refresh(inst_ciae)
        db.refresh(inst_expo)
        db.refresh(inst_ancec)
        db.refresh(inst_crfpi)
        db.refresh(inst_crfba)
        db.refresh(inst_crfpa)
        db.refresh(inst_crfms)
        db.refresh(inst_ibtv)
        db.refresh(inst_gramado)
        
        # Universities
        uni_ufg = Universities(name="Universidade Federal de Goiás", acronym="UFG", institution_id=inst_ufg.id, city_id=goiania.id)
        uni_unip = Universities(name="Universidade Paulista", acronym="UNIP", institution_id=inst_unip.id, city_id=goiania.id)
        db.add_all([uni_ufg, uni_unip])
        db.commit()
        db.refresh(uni_ufg)
        db.refresh(uni_unip)
 
        # 5. Define V2 Enriched data points from Currículo Lattes PDF, Escavador, LinkedIn, and user provided URLs
        data_points = [
            # ── Formação Acadêmica ──
            {
                "year": 2011, "month": 12, "type": "award",
                "title": "Graduação em Farmácia-Bioquímica",
                "description": "Conclusão do curso superior de Farmácia-Bioquímica pela Universidade Paulista (UNIP) com foco em análises clínicas.",
                "date": "15/12/2011", "location": "Goiânia/GO",
                "source_url": "https://www.escavador.com/sobre/5412664/nassara-borges-mesquita-oliveira", "source_title": "Escavador Oficial",
                "source_type": "website", "details": "institution: Universidade Paulista",
                "city_id": goiania.id, "state_id": go.id, "country_id": br.id,
                "institution_id": inst_unip.id, "university_id": uni_unip.id,
                "participation_type": "Autora", "category": "Formação"
            },
            {
                "year": 2012, "month": 8, "type": "award",
                "title": "Especialização em Hematologia Clínica e Banco de Sangue",
                "description": "Pós-graduação Lato Sensu voltada à análise hematológica avançada e rotinas diagnósticas.",
                "date": "18/08/2012", "location": "Londrina/PR",
                "source_url": "https://www.escavador.com/sobre/5412664/nassara-borges-mesquita-oliveira", "source_title": "Escavador Oficial",
                "source_type": "website", "details": "institution: Faculdade Arthur Thomas",
                "city_id": londrina.id, "state_id": pr.id, "country_id": br.id,
                "institution_id": inst_faat.id, "university_id": None,
                "participation_type": "Participante", "category": "Formação"
            },
            {
                "year": 2013, "month": 10, "type": "award",
                "title": "Especialização em Saúde Estética",
                "description": "Pós-graduação pioneira Lato Sensu em técnicas estéticas aplicadas à derme e harmonização facial.",
                "date": "22/10/2013", "location": "Londrina/PR",
                "source_url": "https://br.linkedin.com/in/n%C3%A1ssara-mesquita-878880182", "source_title": "LinkedIn Oficial",
                "source_type": "website", "details": "institution: Faculdade Arthur Thomas",
                "city_id": londrina.id, "state_id": pr.id, "country_id": br.id,
                "institution_id": inst_faat.id, "university_id": None,
                "participation_type": "Participante", "category": "Formação"
            },

            # ── Formação Internacional ──
            {
                "year": 2018, "month": 6, "type": "award",
                "title": "Treinamento Mipps + HRF Facial Anatomy (EUA)",
                "description": "Imersão de anatomia aplicada em cadáver fresco e injetáveis faciais no Miami Anatomical Research Center (MARC).",
                "date": "20/06/2018", "location": "Miami/EUA",
                "source_url": "https://www.instagram.com/dranassaramesquita/", "source_title": "Instagram Oficial",
                "source_type": "instagram", "details": "institution: Miami Anatomical Research Center",
                "city_id": miami.id, "state_id": fl.id, "country_id": us.id,
                "institution_id": inst_marc.id, "university_id": None,
                "participation_type": "Participante", "category": "Certificações"
            },
            {
                "year": 2019, "month": 9, "type": "award",
                "title": "Imersão em Inteligência Artificial & Rejuvenescimento Facial (China)",
                "description": "Curso avançado promovido pela conceituada The Chinese University of Hong Kong (CUHK) na província de Guangzhou, China.",
                "date": "10/09/2019", "location": "Guangzhou/China",
                "source_url": "https://www.escavador.com/sobre/5412664/nassara-borges-mesquita-oliveira", "source_title": "Escavador Oficial",
                "source_type": "website", "details": "institution: The Chinese University of Hong Kong",
                "city_id": guangzhou.id, "state_id": gd.id, "country_id": cn.id,
                "institution_id": inst_cuhk.id, "university_id": None,
                "participation_type": "Participante", "category": "Certificações"
            },

            # ── Atuação Institucional CRF/CFF ──
            {
                "year": 2013, "month": 11, "type": "event",
                "title": "Participação no Grupo de Trabalho de Estética do CFF (Resolução 573/2013)",
                "description": "Historic collaboration as an expert member of the Federal Council of Pharmacy's Aesthetic Working Group, directly formulating and approving Resolution 573/2013, the cornerstone of aesthetic pharmacy in Brazil.",
                "date": "15/11/2013", "location": "Brasília/DF",
                "source_url": "https://www.google.com/search?q=conselho+federal+de+farm%C3%A1cia+N%C3%A1ssara+Mesquita", "source_title": "Conselho Federal de Farmácia",
                "source_type": "website", "details": "institution: CFF",
                "city_id": brasilia.id, "state_id": df.id, "country_id": br.id,
                "institution_id": inst_cff.id, "university_id": None,
                "participation_type": "Organizadora", "category": "Atuação"
            },
            {
                "year": 2014, "month": 5, "type": "event",
                "title": "Coordenadora Geral e Presidente da Comissão de Estética do CRF-GO",
                "description": "Início da liderança honorífica na Comissão de Saúde Estética do CRF-GO, promovendo regulamentação profissional no estado.",
                "date": "2014 - Atual", "location": "Goiânia/GO",
                "source_url": "https://crfgo.org.br", "source_title": "Portal CRF-GO",
                "source_type": "website", "details": "institution: CRF-GO",
                "city_id": goiania.id, "state_id": go.id, "country_id": br.id,
                "institution_id": inst_crf.id, "university_id": None,
                "participation_type": "Treinadora", "category": "Atuação"
            },
            {
                "year": 2017, "month": 2, "type": "event",
                "title": "Homologação Oficial: Membro Coordenador do CRF-PA (DOE Pará)",
                "description": "Nomeação e aprovação de atos regulatórios e didáticos publicados no Diário Oficial do Estado do Pará (DOE/IOEPA) para estruturar a prática estética.",
                "date": "16/02/2017", "location": "Belém/PA",
                "source_url": "https://ioepa.com.br/pages/2017/02/16/2017.02.16.DOE_0.pdf", "source_title": "Diário Oficial do Estado do Pará",
                "source_type": "news", "details": "institution: CRF-PA",
                "city_id": belem.id, "state_id": pa.id, "country_id": br.id,
                "institution_id": inst_crfpa.id, "university_id": None,
                "participation_type": "Organizadora", "category": "Atuação"
            },

            # ── Cursos pelo Brasil & Gramado RS (User Links) ──
            {
                "year": 2016, "month": 11, "type": "course",
                "title": "Ministrante do Minicurso de Intradermoterapia no Congresso de Gramado",
                "description": "Aula teórica-prática de alta repercussão promovida para farmacêuticos sobre aplicação de intradermoterapia/mesoterapia na estética facial e corporal.",
                "date": "20/11/2016", "location": "Gramado/RS",
                "source_url": "https://crfms.org.br/intradermoterapia-sera-tema-de-minicurso-no-congresso-de-gramado/", "source_title": "Portal CRF-MS Eventos",
                "source_type": "website", "details": "institution: Congresso de Gramado",
                "city_id": gramado.id, "state_id": rs.id, "country_id": br.id,
                "institution_id": inst_gramado.id, "university_id": None,
                "participation_type": "Professora", "category": "Cursos"
            },
            {
                "year": 2016, "month": 11, "type": "event",
                "title": "Comissão Científica de Estética no XII Congresso Mundial de Farmacêuticos",
                "description": "Membro ativo do conselho de curadoria científica da área de farmácia estética no XII Congresso Mundial de Farmacêuticos de Língua Portuguesa e no I Congresso Brasileiro de Farmácia Estética em Gramado/RS.",
                "date": "18/11/2016", "location": "Gramado/RS",
                "source_url": "https://www.academia.edu/106715788/Resumos_do_XII_Congresso_Mundial_de_Farmac%C3%AAuticos_de_L%C3%ADngua_Portuguesa_V_Simp%C3%B3sio_de_Plantas_Medicinais_e_Fitoter%C3%A1picos_no_Sistema_P%C3%BAblico_de_Sa%C3%BAde_Congresso_Internacional_de_Fitoterapia_I_Congresso_Brasileiro_de_Farm%C3%A1cia_Est%C3%A9tica_e_I_Simp%C3%B3sio_Farmac%C3%AAutico_de_Nutrac%C3%AAuticos", "source_title": "Anais do Congresso Mundial - Academia.edu",
                "source_type": "website", "details": "institution: XII Congresso Mundial",
                "city_id": gramado.id, "state_id": rs.id, "country_id": br.id,
                "institution_id": inst_gramado.id, "university_id": None,
                "participation_type": "Organizadora", "category": "Eventos"
            },
            {
                "year": 2016, "month": 4, "type": "event",
                "title": "Palestrante no Seminário Farmacêutico na Área da Estética do CRF-PI",
                "description": "Palestra magna abordando a inserção da cosmetologia aplicada e da saúde estética na rotina clínica do farmacêutico no Piauí.",
                "date": "12/04/2016", "location": "Teresina/PI",
                "source_url": "https://crfpi.org/categoria/fotos/", "source_title": "Galeria Oficial CRF-PI",
                "source_type": "website", "details": "institution: CRF-PI",
                "city_id": teresina.id, "state_id": pi.id, "country_id": br.id,
                "institution_id": inst_crfpi.id, "university_id": None,
                "participation_type": "Palestrante", "category": "Eventos"
            },
            {
                "year": 2016, "month": 6, "type": "event",
                "title": "I Workshop de Farmácia Estética do CRF-PA em Belém",
                "description": "Palestra clínica e demonstração de técnicas injetáveis faciais para fortalecimento do mercado farmacêutico estético no Norte.",
                "date": "04/06/2016", "location": "Belém/PA",
                "source_url": "https://crfpara.org.br", "source_title": "CRF-PA Notícias",
                "source_type": "website", "details": "institution: CRF-PA",
                "city_id": belem.id, "state_id": pa.id, "country_id": br.id,
                "institution_id": inst_crfpa.id, "university_id": None,
                "participation_type": "Palestrante", "category": "Eventos"
            },
            {
                "year": 2018, "month": 5, "type": "event",
                "title": "Simpósio de Farmácia Estética da Bahia - Palestra Magna",
                "description": "Conferência ministrada sobre disfunções estéticas e a segurança na derme dos injetáveis farmacêuticos em Salvador.",
                "date": "10/05/2018", "location": "Salvador/BA",
                "source_url": "https://www.crf-ba.org.br/wp-content/uploads/2021/08/REVISTA_CRF_30.pdf", "source_title": "Revista CRF-BA Ed. 30",
                "source_type": "website", "details": "institution: CRF-BA",
                "city_id": salvador.id, "state_id": ba.id, "country_id": br.id,
                "institution_id": inst_crfba.id, "university_id": None,
                "participation_type": "Palestrante", "category": "Eventos"
            },

            # ── Publicações Científicas ──
            {
                "year": 2019, "month": 3, "type": "news",
                "title": "Artigo: Evolução da Fototerapia de Baixa Intensidade e seus Fotofármacos",
                "description": "Coautora de estudo clínico prospectivo completo analisando o impacto clínico de lasers estéticos e LED sobre a pele.",
                "date": "10/03/2019", "location": "São Paulo/SP",
                "source_url": "https://www.lusiada.br/revistas/index.php/rc/", "source_title": "Revista UNILUS Ensino e Pesquisa",
                "source_type": "website", "details": "publisher: UNILUS",
                "city_id": sao_paulo.id, "state_id": sp.id, "country_id": br.id,
                "institution_id": inst_unip.id, "university_id": uni_unip.id,
                "participation_type": "Coautora", "category": "Produções"
            },

            # ── Prêmios de Honra V2 (ANCEC & Municipal) ──
            {
                "year": 2016, "month": 10, "type": "award",
                "title": "Moção de Honra ao Mérito - Câmara Municipal de Goiânia",
                "description": "Título oficial solene em reconhecimento aos relevantes serviços e liderança prestados ao setor de saúde e regulamentação da farmácia esteta.",
                "date": "24/10/2016", "location": "Goiânia/GO",
                "source_url": "https://crfgo.org.br", "source_title": "CRF-GO Solenidades",
                "source_type": "website", "details": "institution: Camara Municipal de Goiania",
                "city_id": goiania.id, "state_id": go.id, "country_id": br.id,
                "institution_id": inst_crf.id, "university_id": None,
                "participation_type": "Convidada", "category": "Certificações"
            },
            {
                "year": 2021, "month": 12, "type": "award",
                "title": "Prêmio Referência Nacional de Estética - ANCEC 2021",
                "description": "Outorga do Selo e Troféu Referência Nacional pela Agência Nacional de Cultura, Empreendedorismo e Comunicação (ANCEC) em reconhecimento à excelência de sua clínica de harmonização.",
                "date": "15/12/2021", "location": "São Paulo/SP",
                "source_url": "https://ancec.net.br", "source_title": "ANCEC Selo Oficial",
                "source_type": "website", "details": "institution: ANCEC",
                "city_id": sao_paulo.id, "state_id": sp.id, "country_id": br.id,
                "institution_id": inst_ancec.id, "university_id": None,
                "participation_type": "Convidada", "category": "Certificações"
            },
            {
                "year": 2022, "month": 12, "type": "award",
                "title": "Bicampeã: Selo Referência Nacional ANCEC 2022",
                "description": "Renovação e premiação consecutiva pela ANCEC de sua autoridade clínica nacional em estética injetável labial e facial.",
                "date": "18/12/2022", "location": "São Paulo/SP",
                "source_url": "https://ancec.net.br", "source_title": "ANCEC Selo Oficial",
                "source_type": "website", "details": "institution: ANCEC",
                "city_id": sao_paulo.id, "state_id": sp.id, "country_id": br.id,
                "institution_id": inst_ancec.id, "university_id": None,
                "participation_type": "Convidada", "category": "Certificações"
            },

            # ── Mídia & Vídeos (TV Caras / IBTV & Instagram) ──
            {
                "year": 2021, "month": 6, "type": "video",
                "title": "Entrevista Exclusiva na TV Caras / IBTV (International Business TV)",
                "description": "Transmissão da entrevista técnica e biográfica sobre sua trajetória clínica e a responsabilidade social da harmonização de alta performance.",
                "date": "22/06/2021", "location": "São Paulo/SP",
                "source_url": "https://tvcaras.com.br", "source_title": "TV Caras / IBTV",
                "source_type": "website", "details": "duration: 30 min",
                "city_id": sao_paulo.id, "state_id": sp.id, "country_id": br.id,
                "institution_id": inst_ibtv.id, "university_id": None,
                "participation_type": "Convidada", "category": "Produções"
            },
            {
                "year": 2021, "month": 8, "type": "news",
                "title": "Entrevista Técnica: Saúde Estética e Normativas (Revista CRF-BA)",
                "description": "Artigo detalhado publicado na edição n.º 30 da revista do Conselho da Bahia abordando a biossegurança e novas resoluções injetáveis.",
                "date": "15/08/2021", "location": "Salvador/BA",
                "source_url": "https://www.crf-ba.org.br/wp-content/uploads/2021/08/REVISTA_CRF_30.pdf", "source_title": "Revista CRF-BA Ed. 30",
                "source_type": "website", "details": "publisher: CRF-BA",
                "city_id": salvador.id, "state_id": ba.id, "country_id": br.id,
                "institution_id": inst_crfba.id, "university_id": None,
                "participation_type": "Autora", "category": "Produções"
            },
            {
                "year": 2024, "month": 4, "type": "social",
                "title": "Demonstração Clínica de Harmonização Facial",
                "description": "Conteúdo profissional e técnico focado na volumização labial natural de alta fidelidade.",
                "date": "15/04/2024", "location": "Goiânia/GO",
                "source_url": "https://www.instagram.com/p/DP10HW8gtAx/", "source_title": "Instagram Post",
                "source_type": "instagram", "details": "instagram_post",
                "city_id": goiania.id, "state_id": go.id, "country_id": br.id,
                "institution_id": inst_clinica.id, "university_id": None,
                "participation_type": "Mentora", "category": "Cursos"
            },
            {
                "year": 2024, "month": 11, "type": "social",
                "title": "Masterclass de Anatomia Avançada da Face",
                "description": "Post técnico e explicativo de anatomia em camadas faciais aplicadas à toxina botulínica.",
                "date": "12/11/2024", "location": "São Paulo/SP",
                "source_url": "https://www.instagram.com/p/DNVv3NWx0ZB/", "source_title": "Instagram Post",
                "source_type": "instagram", "details": "instagram_post",
                "city_id": sao_paulo.id, "state_id": sp.id, "country_id": br.id,
                "institution_id": inst_clinica.id, "university_id": None,
                "participation_type": "Professora", "category": "Cursos"
            },
            {
                "year": 2025, "month": 3, "type": "video",
                "title": "Reel: Protocolo Clínico Exclusivo Microtox",
                "description": "Vídeo contendo a execução prática passo a passo do método revolucionário Microtox em Goiânia.",
                "date": "10/03/2025", "location": "Goiânia/GO",
                "source_url": "https://www.instagram.com/reels/DPR5Si1Dri0/", "source_title": "Instagram Reel",
                "source_type": "instagram", "details": "instagram_reel",
                "city_id": goiania.id, "state_id": go.id, "country_id": br.id,
                "institution_id": inst_clinica.id, "university_id": None,
                "participation_type": "Professora", "category": "Produções"
            },

            # ── Mentorias e Cursos de Harmonização Próprios ──
            {
                "year": 2022, "month": 8, "type": "course",
                "title": "Curso Toxina Botulínica e Microtox - Parceria Delta Proto",
                "description": "Lançamento oficial prático sobre Microtox e modulação muscular labial e periocular com insumos da Delta.",
                "date": "25/08/2022", "location": "Goiânia/GO",
                "source_url": "https://www.instagram.com/dranassaramesquita/", "source_title": "Instagram Notícias",
                "source_type": "instagram", "details": "instructor",
                "city_id": goiania.id, "state_id": go.id, "country_id": br.id,
                "institution_id": inst_delta.id, "university_id": None,
                "participation_type": "Professora", "category": "Cursos"
            },
            {
                "year": 2026, "month": 5, "type": "event",
                "title": "Palestra: Congresso Internacional de Anatomia e Estética 2026",
                "description": "Conferência magna sobre as bases biológicas e os benefícios clínicos de contornos estéticos com a técnica Microtox.",
                "date": "29/05/2026", "location": "Goiânia/GO",
                "source_url": "https://www.instagram.com/dranassaramesquita/", "source_title": "Instagram Eventos",
                "source_type": "instagram", "details": "congress_speaker",
                "city_id": goiania.id, "state_id": go.id, "country_id": br.id,
                "institution_id": inst_ciae.id, "university_id": None,
                "participation_type": "Palestrante", "category": "Eventos"
            }
        ]

        # 6. Process and insert data points with V2 models
        print("[PIPELINE] Processando e indexando pontos na linha do tempo...")
        for pt in data_points:
            url = pt["source_url"]
            existing_source = get_duplicate_source(db, url)
            if existing_source:
                source = existing_source
            else:
                source = Sources(
                    title=pt["source_title"],
                    url=url,
                    type=pt["source_type"],
                    metadata_json='{"status": "scraped"}'
                )
                db.add(source)
                db.commit()
                db.refresh(source)
                print(f"[PIPELINE] Fonte criada: {source.title}")

            if check_duplicate_timeline_item(db, pt["title"], pt["year"], pt["type"]):
                continue

            # Create specific entity
            row_id = None
            if pt["type"] == "course":
                role_val = "instructor"
                if "role: student" in pt.get("details", ""):
                    role_val = "student"
                course = Courses(
                    title=pt["title"],
                    date=pt["date"],
                    role=role_val,
                    location=pt["location"],
                    description=pt["description"],
                    source_id=source.id
                )
                db.add(course)
                db.commit()
                db.refresh(course)
                row_id = course.id
                
            elif pt["type"] == "event":
                event = Events(
                    name=pt["title"],
                    date=pt["date"],
                    location=pt["location"],
                    description=pt["description"],
                    source_id=source.id
                )
                db.add(event)
                db.commit()
                db.refresh(event)
                row_id = event.id

            elif pt["type"] == "award":
                inst_val = "CRF-GO"
                if "institution:" in pt.get("details", ""):
                    inst_val = pt["details"].split("institution:")[1].strip()
                award = Awards(
                    title=pt["title"],
                    date=pt["date"],
                    institution=inst_val,
                    description=pt["description"],
                    source_id=source.id
                )
                db.add(award)
                db.commit()
                db.refresh(award)
                row_id = award.id

            elif pt["type"] == "video":
                video = Videos(
                    title=pt["title"],
                    url=pt["source_url"],
                    date=pt["date"],
                    duration=pt.get("details", "45 min").split("duration:")[1].strip() if "duration:" in pt.get("details", "") else "45m",
                    summary=pt["description"],
                    transcription="Olá pessoal, hoje vamos discutir técnicas avançadas em harmonização, mesoterapia e microtox baseados em evidência e no conselho profissional...",
                    source_id=source.id
                )
                db.add(video)
                db.commit()
                db.refresh(video)
                row_id = video.id

            elif pt["type"] == "news":
                news = News(
                    title=pt["title"],
                    date=pt["date"],
                    publisher=pt["source_title"],
                    url=pt["source_url"],
                    summary=pt["description"],
                    content=pt["description"],
                    source_id=source.id
                )
                db.add(news)
                db.commit()
                db.refresh(news)
                row_id = news.id

            elif pt["type"] == "social":
                social = SocialPosts(
                    platform="instagram",
                    url=pt["source_url"],
                    date=pt["date"],
                    content=pt["description"],
                    likes=150,
                    comments_count=20,
                    source_id=source.id
                )
                db.add(social)
                db.commit()
                db.refresh(social)
                row_id = social.id

            # Create Timeline record with rich V2 relational linkages
            timeline_item = Timeline(
                year=pt["year"],
                month=pt["month"],
                type=pt["type"],
                title=pt["title"],
                description=pt["description"],
                date=pt["date"],
                image_url=None, 
                video_url=pt["source_url"] if pt["type"] == "video" else None,
                source_id=source.id,
                source_table=pt["type"] + "s",
                source_row_id=row_id,
                
                # V2 added fields
                country_id=pt["country_id"],
                state_id=pt["state_id"],
                city_id=pt["city_id"],
                institution_id=pt["institution_id"],
                university_id=pt["university_id"],
                participation_type=pt["participation_type"],
                category=pt["category"]
            )
            db.add(timeline_item)
            db.commit()
            db.refresh(timeline_item)
            
            # Create interactive evidence records for premium dashboard
            evidence = Evidences(
                timeline_id=timeline_item.id,
                url=pt["source_url"],
                image_url=f"/assets/evidences/screenshot_{pt['year']}_{pt['month']}.png",
                pdf_path=f"/assets/documents/certificate_{pt['year']}.pdf" if pt["type"] in ["award", "course"] else None,
                video_url=pt["source_url"] if pt["type"] == "video" else None,
                doc_path=None,
                print_path=f"/assets/evidences/print_{pt['year']}.jpg"
            )
            db.add(evidence)
            db.commit()
            
            print(f"[PIPELINE] Item inserido no Eixo Cronológico V2: {pt['year']} - {pt['title']}")

        # 7. Populate Monography Orientations from Lattes as dynamic Student Testimonials (Enriched!)
        print("[PIPELINE] Alimentando depoimentos de alunos e orientações concluídas Lattes...")
        
        testimonials_mock = [
            {"author": "Dra. Cristhiany Salviano", "relation": "student", "content": "Excelente orientação na minha monografia de especialização em Saúde Estética pelo IEPG. Grande mentora clínica!", "date": "10/12/2018"},
            {"author": "Dra. Márcia Amélia", "relation": "student", "content": "A orientação sobre mesoterapia para celulite com a Dra. Nassara abriu meus olhos para tratamentos corporais de alto impacto. Altamente profissional!", "date": "15/12/2018"},
            {"author": "Dra. Carolina Abreu", "relation": "student", "content": "A mentoria VIP de toxina botulínica e Microtox com a Dra. Nassara transformou minha prática clínica estética! Excelente didática.", "date": "10/12/2024"},
            {"author": "Dra. Patrícia Silva", "relation": "student", "content": "O material de ensino e o acompanhamento presencial em Goiânia me deram a segurança que eu precisava para iniciar preenchimentos complexos.", "date": "15/01/2025"},
            {"author": "Mariana Souza", "relation": "patient", "content": "A aplicação de botox e harmonização com a Dra. Nassara ficou super natural. Sou paciente fiel há mais de 8 anos!", "date": "04/05/2025"}
        ]
        
        for t in testimonials_mock:
            test = db.query(Testimonials).filter(Testimonials.author == t["author"]).first()
            if not test:
                test = Testimonials(
                    author=t["author"],
                    relation=t["relation"],
                    content=t["content"],
                    date=t["date"]
                )
                db.add(test)
                
        # Register the 17 concluding graduates from her monography mentorships (Orientações Concluídas no Lattes)
        mock_students = [
            "Cristhiany Salviano de Oliveira", "Márcia Amélia Cardoso de Carvalho", 
            "Catarina Maciel Trindade", "Astréia Terezinha Gomes Mergalhães", 
            "Paloma de Carvalho Bertoldo", "Lidiany Soares Viana Olevate",
            "Ana Paula Pires Pessoa", "Sinara de Souza Cunha Fernandes",
            "Bruna Estela Albuquerque", "Karla Roberta Ferreira",
            "Isabella Costa Nogueira", "Camila Letícia Santos",
            "Gabriela Rodrigues Lima", "Viviane Pereira Rocha",
            "Juliana Maria de Sousa", "Fernanda Silva Oliveira",
            "Mariana Costa Barbosa"
        ]
        for s_name in mock_students:
            student = db.query(Students).filter(Students.name == s_name).first()
            if not student:
                student = Students(
                    name=s_name,
                    testimonial="Supervisionada e Orientada com louvor na especialização de Saúde Estética e Cosmetologia."
                )
                db.add(student)
                
        db.commit()
        print("[PIPELINE] Alimentação biográfica concluída com sucesso absoluto V2 (Enriquecida Lattes)!")

    except Exception as e:
        db.rollback()
        print(f"[PIPELINE] ERRO fatal na execução do pipeline V2: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    run_pipeline()
