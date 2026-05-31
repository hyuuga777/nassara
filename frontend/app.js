// ── Front-End Application Controller V2 ──

const API_BASE_URL = "http://127.0.0.1:8000";

// SPA & Timeline State Management
let timelineData = [];
let relevanceData = {};
let currentSection = "overview";
let displayMode = "standard"; // "standard" or "hierarchical"

// Client-Side Facet State
let selectedYear = null;
let selectedCategory = null;
let selectedLocation = null; // code or name
let selectedParticipation = null;
let selectedInstitution = null;

// DOM Elements
const sections = document.querySelectorAll(".view-section");
const navItems = document.querySelectorAll(".nav-item");
const pageTitle = document.getElementById("main-page-title");
const searchInput = document.getElementById("global-search-input");
const btnSyncPipeline = document.getElementById("btn-sync-pipeline");
const modal = document.getElementById("transcription-modal");
const btnCloseModal = document.getElementById("btn-close-modal");

// ── Application Initialization ──
document.addEventListener("DOMContentLoaded", () => {
    initNavigation();
    loadProfile();
    loadRelevanceMetrics();
    loadDashboardTestimonials();
    loadTimelineData();
    initSyncButton();
    initSearch();
    initModalClose();
    initTimelineModeButtons();
    initClearFiltersButton();
    initPresenceMap();
});

// ── SPA Navigation ──
function initNavigation() {
    navItems.forEach(item => {
        item.addEventListener("click", () => {
            const sectionId = item.getAttribute("data-section");
            switchSection(sectionId);
            
            navItems.forEach(nav => nav.classList.remove("active"));
            item.classList.add("active");
        });
    });
}

function switchSection(sectionId) {
    currentSection = sectionId;
    sections.forEach(sec => sec.classList.remove("active-section"));
    
    const targetSection = document.getElementById(`section-${sectionId}`);
    if (targetSection) {
        targetSection.classList.add("active-section");
    }
    
    const titleMap = {
        "overview": "Painel de Investigação Biográfica",
        "timeline": "Eixo Cronológico Profissional (2013 - 2026)",
        "lattes": "Currículo Lattes Acadêmico & Profissional",
        "map": "Mapa de Presença Geográfica Dra. Nássara Mesquita",
        "courses": "Cursos Ministrados & Realizados",
        "events": "Congressos, Workshops & Palestras",
        "videos": "Vídeos, Lives & Podcasts Transcrevidos",
        "news": "Notícias & Presença na Imprensa",
        "testimonials": "Depoimentos de Pacientes & Mentoria",
        "sources": "Fontes de Dados Públicas Indexadas"
    };
    pageTitle.textContent = titleMap[sectionId] || "Memorial Digital";
    
    if (sectionId === "courses") loadCoursesGrid();
    if (sectionId === "events") loadEventsGrid();
    if (sectionId === "videos") loadVideosGrid();
    if (sectionId === "news") loadNewsGrid();
    if (sectionId === "testimonials") loadTestimonialsSection();
    if (sectionId === "sources") loadSourcesTable();
    if (sectionId === "lattes") loadLattesCurriculum();
    if (sectionId === "map") renderPresenceMapDashboard();
}

// ── API Loaders & Rendering ──

async function loadProfile() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/profile`);
        if (response.ok) {
            const data = await response.json();
            document.getElementById("bio-summary-text").textContent = data.bio;
            
            // Render rich quick tags including CPF and Instagram if metadata_json is present
            if (data.metadata_json) {
                const meta = JSON.parse(data.metadata_json);
                const tagsContainer = document.querySelector(".bio-quick-tags");
                if (tagsContainer) {
                    tagsContainer.innerHTML = `
                        <span class="tag-item"><i class="fa-solid fa-award"></i> Farmácia Estética</span>
                        <span class="tag-item"><i class="fa-solid fa-syringe"></i> Referência em Toxina & Microtox</span>
                        <span class="tag-item"><i class="fa-solid fa-location-dot"></i> Goiânia/GO</span>
                        ${meta.instagram ? `<span class="tag-item"><i class="fa-brands fa-instagram"></i> ${meta.instagram}</span>` : ''}
                        ${meta.cpf ? `<span class="tag-item"><i class="fa-solid fa-id-card"></i> CPF: ${meta.cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4")}</span>` : ''}
                        ${meta.crf ? `<span class="tag-item"><i class="fa-solid fa-file-medical"></i> ${meta.crf}</span>` : ''}
                    `;
                }
            }
        }
    } catch (e) {
        console.error("Falha ao carregar perfil profissional:", e);
    }
}

async function loadRelevanceMetrics() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/relevance`);
        if (response.ok) {
            relevanceData = await response.json();
            
            animateValue("count-courses", 0, relevanceData.total_courses, 1200);
            animateValue("count-events", 0, relevanceData.total_events, 1200);
            animateValue("count-news", 0, relevanceData.total_news, 1200);
            animateValue("count-videos", 0, relevanceData.total_videos, 1200);
            
            const score = relevanceData.total_appearances;
            document.getElementById("relevance-score-index").textContent = score;
            
            const percentage = Math.min((score / 150) * 100, 100);
            const outerCircle = document.querySelector(".gauge-circle-outer");
            outerCircle.style.background = `conic-gradient(var(--color-gold) 0% ${percentage}%, rgba(255, 255, 255, 0.05) ${percentage}% 100%)`;
            
            const badge = document.getElementById("relevance-badge");
            if (score > 100) {
                badge.textContent = "Autoridade Nacional Destaque";
                badge.style.color = "var(--color-gold)";
                badge.style.backgroundColor = "rgba(197, 168, 128, 0.12)";
                badge.style.borderColor = "rgba(197, 168, 128, 0.3)";
            } else if (score > 50) {
                badge.textContent = "Referência Regional Forte";
                badge.style.color = "var(--color-blue)";
                badge.style.backgroundColor = "rgba(29, 130, 245, 0.12)";
                badge.style.borderColor = "rgba(29, 130, 245, 0.3)";
            } else {
                badge.textContent = "Presença Local Consolidada";
                badge.style.color = "var(--color-green)";
            }
        }
    } catch (e) {
        console.error("Falha ao carregar métricas de relevância:", e);
    }
}

async function loadDashboardTestimonials() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/testimonials`);
        if (response.ok) {
            const data = await response.json();
            const container = document.getElementById("dashboard-testimonial-container");
            container.innerHTML = "";
            
            if (data.length === 0) {
                container.innerHTML = `<p class="testimonial-text">Nenhum depoimento catalogado.</p>`;
                return;
            }
            
            data.forEach((item, index) => {
                const slide = document.createElement("div");
                slide.className = `testimonial-slide ${index === 0 ? 'active' : ''}`;
                slide.innerHTML = `
                    <p class="testimonial-text">"${item.content}"</p>
                    <span class="testimonial-author">${item.author} (${translateRelation(item.relation)})</span>
                `;
                container.appendChild(slide);
            });
            
            initTestimonialRotation();
        }
    } catch (e) {
        console.error("Erro ao carregar depoimentos do dashboard:", e);
    }
}

async function loadTimelineData() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/timeline`);
        if (response.ok) {
            timelineData = await response.json();
            renderTimelineView();
        }
    } catch (e) {
        console.error("Erro ao carregar eixo cronológico:", e);
    }
}

// ── V2 UPDATE: Chronology Filters & Facet Sidebar rendering ──

function renderFacetsSidebar(filteredItems) {
    const rawItems = timelineData;
    
    // 1. Calculate facet counts
    const years = {};
    const categories = {};
    const locations = {};
    const participations = {};
    const institutions = {};
    
    rawItems.forEach(item => {
        // Year
        years[item.year] = (years[item.year] || 0) + 1;
        // Category
        if (item.category) {
            categories[item.category] = (categories[item.category] || 0) + 1;
        }
        // Location (City/State)
        if (item.city && item.state) {
            const locName = `${item.city.name}/${item.state.code}`;
            locations[locName] = (locations[locName] || 0) + 1;
        }
        // Participation
        if (item.participation_type) {
            participations[item.participation_type] = (participations[item.participation_type] || 0) + 1;
        }
        // Institution
        if (item.institution) {
            const instName = item.institution.acronym || item.institution.name;
            institutions[instName] = (institutions[instName] || 0) + 1;
        }
    });

    // 2. Render Years Facet
    renderFacetSection("facet-years", years, selectedYear, (val) => {
        selectedYear = selectedYear === val ? null : val;
        renderTimelineView();
    });
    
    // 3. Render Category Facet
    renderFacetSection("facet-categories", categories, selectedCategory, (val) => {
        selectedCategory = selectedCategory === val ? null : val;
        renderTimelineView();
    });

    // 4. Render Location Facet
    renderFacetSection("facet-locations", locations, selectedLocation, (val) => {
        selectedLocation = selectedLocation === val ? null : val;
        renderTimelineView();
    });

    // 5. Render Participation Facet
    renderFacetSection("facet-participation", participations, selectedParticipation, (val) => {
        selectedParticipation = selectedParticipation === val ? null : val;
        renderTimelineView();
    });

    // 6. Render Institution Facet
    renderFacetSection("facet-institutions", institutions, selectedInstitution, (val) => {
        selectedInstitution = selectedInstitution === val ? null : val;
        renderTimelineView();
    });
}

function renderFacetSection(elementId, facetsObj, activeVal, onClickCallback) {
    const container = document.getElementById(elementId);
    if (!container) return;
    container.innerHTML = "";
    
    const sortedKeys = Object.keys(facetsObj).sort((a, b) => b.localeCompare(a, undefined, { numeric: true }));
    
    sortedKeys.forEach(key => {
        const count = facetsObj[key];
        const chip = document.createElement("button");
        chip.className = `filter-chip ${activeVal == key ? 'active' : ''}`;
        chip.innerHTML = `
            <span>${key}</span>
            <span class="filter-chip-count">${count}</span>
        `;
        chip.addEventListener("click", () => onClickCallback(key));
        container.appendChild(chip);
    });
}

function initTimelineModeButtons() {
    const btnStandard = document.getElementById("btn-mode-standard");
    const btnHierarchical = document.getElementById("btn-mode-hierarchical");
    
    if (btnStandard && btnHierarchical) {
        btnStandard.addEventListener("click", () => {
            btnStandard.classList.add("active");
            btnHierarchical.classList.remove("active");
            displayMode = "standard";
            renderTimelineView();
        });
        
        btnHierarchical.addEventListener("click", () => {
            btnHierarchical.classList.add("active");
            btnStandard.classList.remove("active");
            displayMode = "hierarchical";
            renderTimelineView();
        });
    }
}

function initClearFiltersButton() {
    const btnClear = document.getElementById("btn-clear-all-filters");
    if (btnClear) {
        btnClear.addEventListener("click", () => {
            selectedYear = null;
            selectedCategory = null;
            selectedLocation = null;
            selectedParticipation = null;
            selectedInstitution = null;
            renderTimelineView();
        });
    }
}

function getFilteredTimelineData() {
    return timelineData.filter(item => {
        if (selectedYear && item.year != selectedYear) return false;
        if (selectedCategory && item.category != selectedCategory) return false;
        if (selectedLocation) {
            const locName = item.city && item.state ? `${item.city.name}/${item.state.code}` : "";
            if (locName != selectedLocation) return false;
        }
        if (selectedParticipation && item.participation_type != selectedParticipation) return false;
        if (selectedInstitution) {
            const instName = item.institution ? (item.institution.acronym || item.institution.name) : "";
            if (instName != selectedInstitution) return false;
        }
        return true;
    });
}

// Render primary Timeline (standard vs hierarchical)
function renderTimelineView() {
    const filtered = getFilteredTimelineData();
    renderFacetsSidebar(filtered);
    
    const container = document.getElementById("timeline-list-container");
    if (!container) return;
    container.innerHTML = "";
    
    const activeTimelineSection = document.getElementById("timeline-scroll-axis");
    if (activeTimelineSection) {
        // Toggle the visual line class based on mode
        if (displayMode === "hierarchical") {
            activeTimelineSection.classList.remove("timeline-container");
        } else {
            activeTimelineSection.classList.add("timeline-container");
        }
    }
    
    if (filtered.length === 0) {
        container.innerHTML = `<p class="text-muted" style="margin-left: 20px;">Nenhum registro encontrado para a combinação de filtros selecionada.</p>`;
        return;
    }
    
    if (displayMode === "standard") {
        // Render chronological timeline card list
        filtered.forEach((item, index) => {
            const card = document.createElement("div");
            card.className = "timeline-item-card glass-panel hover-grow animate-fade-in";
            card.style.animationDelay = `${index * 0.03}s`;
            
            const dot = document.createElement("div");
            dot.className = "timeline-dot";
            card.appendChild(dot);
            
            // Build card inner elements and evidences
            let evidencesHtml = "";
            if (item.evidences && item.evidences.length > 0) {
                evidencesHtml = `<div class="evidences-list">`;
                item.evidences.forEach(ev => {
                    if (ev.url) {
                        evidencesHtml += `<a href="${ev.url}" target="_blank" class="evidence-badge"><i class="fa-solid fa-link"></i> Fonte Digital</a>`;
                    }
                    if (ev.pdf_path) {
                        evidencesHtml += `<span class="evidence-badge"><i class="fa-solid fa-file-pdf"></i> Certificado PDF</span>`;
                    }
                    if (ev.image_url) {
                        evidencesHtml += `<span class="evidence-badge"><i class="fa-solid fa-image"></i> Evidência Print</span>`;
                    }
                });
                evidencesHtml += `</div>`;
            }
            
            card.innerHTML += `
                <div class="timeline-meta">
                    <span class="timeline-year-badge">${item.year}</span>
                    <span class="timeline-cat-badge">${item.category || translateType(item.type)} ${item.participation_type ? `• ${item.participation_type}` : ''}</span>
                </div>
                <h4 class="timeline-title">${item.title}</h4>
                <p class="timeline-desc">${item.description || ''}</p>
                <div class="timeline-footer">
                    <span class="timeline-loc"><i class="fa-solid fa-location-dot"></i> ${item.date || ''} ${item.city ? `(${item.city.name}/${item.state.code})` : ''}</span>
                    ${item.video_url ? `<a href="#" class="timeline-link btn-view-transcription" data-id="${item.source_row_id}"><i class="fa-solid fa-play"></i> Ver Vídeo & Transcrição</a>` : ''}
                </div>
                ${evidencesHtml}
            `;
            
            container.appendChild(card);
        });
    } else {
        // ── Hierarchical Rendering: Year -> Month -> Event ──
        // Group items by year
        const yearGroups = {};
        filtered.forEach(item => {
            if (!yearGroups[item.year]) {
                yearGroups[item.year] = {};
            }
            const mKey = item.month || 12; // Fallback to Dec
            if (!yearGroups[item.year][mKey]) {
                yearGroups[item.year][mKey] = [];
            }
            yearGroups[item.year][mKey].push(item);
        });
        
        // Sort years descending
        const sortedYears = Object.keys(yearGroups).sort((a, b) => b - a);
        
        sortedYears.forEach(year => {
            const yearGroupDiv = document.createElement("div");
            yearGroupDiv.className = "timeline-year-group";
            
            yearGroupDiv.innerHTML = `
                <div class="timeline-year-header">
                    <div class="timeline-year-title">${year}</div>
                    <div class="timeline-year-line"></div>
                </div>
            `;
            
            const months = yearGroups[year];
            // Sort months descending
            const sortedMonths = Object.keys(months).sort((a, b) => b - a);
            
            sortedMonths.forEach(month => {
                const monthGroupDiv = document.createElement("div");
                monthGroupDiv.className = "timeline-month-group";
                
                monthGroupDiv.innerHTML = `
                    <div class="timeline-month-header">${getMonthName(month)}</div>
                `;
                
                months[month].forEach(item => {
                    const card = document.createElement("div");
                    card.className = "timeline-item-card glass-panel hover-grow";
                    card.style.margin = "0 0 16px 0";
                    card.style.padding = "16px";
                    
                    let evidencesHtml = "";
                    if (item.evidences && item.evidences.length > 0) {
                        evidencesHtml = `<div class="evidences-list">`;
                        item.evidences.forEach(ev => {
                            if (ev.url) {
                                evidencesHtml += `<a href="${ev.url}" target="_blank" class="evidence-badge"><i class="fa-solid fa-link"></i> Fonte</a>`;
                            }
                            if (ev.pdf_path) {
                                evidencesHtml += `<span class="evidence-badge"><i class="fa-solid fa-file-pdf"></i> Certificado</span>`;
                            }
                        });
                        evidencesHtml += `</div>`;
                    }
                    
                    card.innerHTML = `
                        <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:11px; color:var(--text-muted);">
                            <span>${item.category || translateType(item.type)}</span>
                            <span>${item.participation_type || ''}</span>
                        </div>
                        <h5 class="timeline-title" style="font-size:14px; margin-bottom:6px;">${item.title}</h5>
                        <p class="timeline-desc" style="font-size:12px; margin-bottom:10px;">${item.description || ''}</p>
                        <div style="display:flex; justify-content:space-between; align-items:center; font-size:11px; color:var(--text-muted);">
                            <span><i class="fa-solid fa-location-dot"></i> ${item.city ? `${item.city.name}/${item.state.code}` : item.date}</span>
                            ${item.video_url ? `<a href="#" class="timeline-link btn-view-transcription" data-id="${item.source_row_id}"><i class="fa-solid fa-play"></i> Vídeo</a>` : ''}
                        </div>
                        ${evidencesHtml}
                    `;
                    monthGroupDiv.appendChild(card);
                });
                yearGroupDiv.appendChild(monthGroupDiv);
            });
            container.appendChild(yearGroupDiv);
        });
    }
    
    bindVideoTriggers();
}

// ── V2 UPDATE: Lattes Curriculum Compilation ──

async function loadLattesCurriculum() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/lattes`);
        if (response.ok) {
            const data = await response.json();
            
            // Populate Lattes sections
            populateLattesSection("lattes-content-formacao", data.formacao, "Nenhuma formação registrada.");
            populateLattesSection("lattes-content-atuacao", data.atuacao, "Nenhuma atuação profissional registrada.");
            populateLattesSection("lattes-content-producoes", data.producoes, "Nenhuma produção registrada.");
            populateLattesSection("lattes-content-eventos", data.eventos, "Nenhum evento registrado.");
            populateLattesSection("lattes-content-cursos", data.cursos, "Nenhum curso registrado.");
            populateLattesSection("lattes-content-orientacoes", data.orientacoes, "Nenhuma orientação registrada.");
            populateLattesSection("lattes-content-certificacoes", data.certificacoes, "Nenhuma certificação registrada.");
        }
    } catch (e) {
        console.error("Falha ao compilar Currículo Lattes:", e);
    }
}

function populateLattesSection(elementId, itemsList, emptyMessage) {
    const container = document.getElementById(elementId);
    if (!container) return;
    container.innerHTML = "";
    
    if (!itemsList || itemsList.length === 0) {
        container.innerHTML = `<p class="text-muted" style="font-size:12px; font-style:italic;">${emptyMessage}</p>`;
        return;
    }
    
    itemsList.forEach(item => {
        const div = document.createElement("div");
        div.className = "lattes-item";
        
        let details = "";
        if (item.institution) {
            details += ` no(a) <strong>${item.institution}</strong>`;
        }
        if (item.university) {
            details += ` (${item.university})`;
        }
        if (item.location) {
            details += `, <em>${item.location}</em>`;
        }
        if (item.participation_type) {
            details += ` [Participação: <strong>${item.participation_type}</strong>]`;
        }
        
        div.innerHTML = `
            <span class="lattes-item-year">${item.year} - ${item.month ? `${item.month.toString().padStart(2, '0')}/` : ''}${item.year}</span>
            <span><strong>${item.title}</strong>. ${item.description || ''}${details}.</span>
        `;
        container.appendChild(div);
    });
}

// ── V2 UPDATE: Presence Map Controller ──

let mapScope = "brasil";

function initPresenceMap() {
    const mapToggleBtns = document.querySelectorAll(".map-toggle-btn");
    mapToggleBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            mapToggleBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            mapScope = btn.getAttribute("data-scope");
            renderPresenceMapDashboard();
        });
    });
}

function renderPresenceMapDashboard() {
    const listContainer = document.getElementById("map-geo-cards-list");
    if (!listContainer) return;
    listContainer.innerHTML = "";
    
    // Group timeline data by city to produce dynamic geographic details cards
    const citiesCount = {};
    timelineData.forEach(item => {
        if (item.city) {
            const cityName = item.city.name;
            if (!citiesCount[cityName]) {
                citiesCount[cityName] = {
                    city: item.city.name,
                    state: item.state.code,
                    country: item.country.name,
                    itemsCount: 0,
                    details: []
                };
            }
            citiesCount[cityName].itemsCount += 1;
            citiesCount[cityName].details.push(`${item.year} - ${item.title}`);
        }
    });

    // Stylize visual map marker opacity based on active mapScope selection
    const markerGoiania = document.getElementById("marker-goiania");
    const markerSaopaulo = document.getElementById("marker-saopaulo");
    const markerMiami = document.getElementById("marker-miami");

    if (markerGoiania && markerSaopaulo && markerMiami) {
        if (mapScope === "brasil") {
            markerGoiania.style.display = "block";
            markerSaopaulo.style.display = "block";
            markerMiami.style.display = "none";
        } else if (mapScope === "latam") {
            markerGoiania.style.display = "block";
            markerSaopaulo.style.display = "block";
            markerMiami.style.display = "none";
        } else {
            markerGoiania.style.display = "block";
            markerSaopaulo.style.display = "block";
            markerMiami.style.display = "block";
        }
    }

    const sortedCities = Object.values(citiesCount).sort((a, b) => b.itemsCount - a.itemsCount);
    
    // Filter displayed list cards based on mapScope
    const filteredCities = sortedCities.filter(c => {
        if (mapScope === "brasil" && c.country !== "Brasil") return false;
        if (mapScope === "latam" && c.country !== "Brasil") return false; // In this dataset only Brazil represents Latam
        return true;
    });

    if (filteredCities.length === 0) {
        listContainer.innerHTML = `<p class="text-muted" style="font-size:12px;">Nenhuma localidade indexada para este escopo.</p>`;
        return;
    }

    filteredCities.forEach(c => {
        const card = document.createElement("div");
        card.className = "geo-card";
        card.innerHTML = `
            <div class="geo-card-header">
                <span class="geo-card-title">${c.city} - ${c.state}</span>
                <span class="geo-card-stat">${c.itemsCount} ${c.itemsCount === 1 ? 'Registro' : 'Registros'}</span>
            </div>
            <div class="geo-card-detail">
                ${c.details.slice(0, 3).map(d => `• ${d}`).join('<br>')}
                ${c.details.length > 3 ? `<br>• e mais ${c.details.length - 3} registros...` : ''}
            </div>
        `;
        
        // Setup marker highlights on card hover
        card.addEventListener("mouseenter", () => {
            highlightMarker(c.city.toLowerCase());
        });
        
        listContainer.appendChild(card);
    });
}

function highlightMarker(cityName) {
    // Reset all scale styles
    document.querySelectorAll(".map-marker-node").forEach(node => {
        node.querySelector(".marker-core").setAttribute("r", "5");
    });
    
    const node = document.getElementById(`marker-${cityName.replace("ã", "a").replace(" ", "")}`);
    if (node) {
        node.querySelector(".marker-core").setAttribute("r", "8");
    }
}

// Bind SVG markers hovers & tooltips
function initInteractiveMapTriggers() {
    const tooltip = document.getElementById("map-presence-tooltip");
    
    const markers = {
        "goiania": { title: "Goiânia - GO, Brasil", desc: "Sede principal clínica, 11 registros cronológicos indexados (Cursos, Eventos, Prêmios)." },
        "saopaulo": { title: "São Paulo - SP, Brasil", desc: "Pólo secundário de mentorias e especializações de luxo da Dra. Nássara Mesquita (2 registros)." },
        "miami": { title: "Miami - Flórida, EUA", desc: "Certificação internacional de anatomia em cadáver fresco no Miami Anatomical Research Center." }
    };
    
    Object.keys(markers).forEach(key => {
        const node = document.getElementById(`marker-${key}`);
        if (node) {
            node.addEventListener("mouseenter", (e) => {
                tooltip.querySelector(".tooltip-city").textContent = markers[key].title;
                tooltip.querySelector(".tooltip-desc").textContent = markers[key].desc;
                
                tooltip.classList.add("active");
                
                // Position tooltip relative to marker coordinates inside SVGs
                const rect = node.getBoundingClientRect();
                const parentRect = node.ownerSVGElement.getBoundingClientRect();
                
                tooltip.style.left = `${rect.left - parentRect.left + 20}px`;
                tooltip.style.top = `${rect.top - parentRect.top - 20}px`;
            });
            
            node.addEventListener("mouseleave", () => {
                tooltip.classList.remove("active");
            });
        }
    });
}

// Trigger tooltips bind on map view load
function initPresenceMap() {
    const mapToggleBtns = document.querySelectorAll(".map-toggle-btn");
    mapToggleBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            mapToggleBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            mapScope = btn.getAttribute("data-scope");
            renderPresenceMapDashboard();
        });
    });
    
    initInteractiveMapTriggers();
}


// ── Course & Mentoria Grid Loader ──
async function loadCoursesGrid() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/courses`);
        if (response.ok) {
            const data = await response.json();
            const container = document.getElementById("courses-grid-container");
            container.innerHTML = "";
            
            data.forEach((item, index) => {
                const card = document.createElement("div");
                card.className = "item-card glass-panel hover-grow animate-fade-in";
                card.style.animationDelay = `${index * 0.05}s`;
                card.innerHTML = `
                    <span class="badge-gold">${item.role === 'instructor' ? 'CURSO MINISTRADO' : 'REALIZADO'}</span>
                    <h4 class="item-title">${item.title}</h4>
                    <p class="item-desc">${item.description || ''}</p>
                    <div class="card-footer-info">
                        <span><i class="fa-solid fa-calendar"></i> ${item.date || ''}</span>
                        <span><i class="fa-solid fa-location-dot"></i> ${item.location || ''}</span>
                    </div>
                `;
                container.appendChild(card);
            });
        }
    } catch (e) {
        console.error("Falha ao carregar grid de cursos:", e);
    }
}

// ── Events Grid Loader ──
async function loadEventsGrid() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/events`);
        if (response.ok) {
            const data = await response.json();
            const container = document.getElementById("events-grid-container");
            container.innerHTML = "";
            
            data.forEach((item, index) => {
                const card = document.createElement("div");
                card.className = "item-card glass-panel hover-grow animate-fade-in";
                card.style.animationDelay = `${index * 0.05}s`;
                card.innerHTML = `
                    <span class="badge-gold">CONGRESSO / WORKSHOP</span>
                    <h4 class="item-title">${item.name}</h4>
                    <p class="item-desc">${item.description || ''}</p>
                    <div class="card-footer-info">
                        <span><i class="fa-solid fa-calendar"></i> ${item.date || ''}</span>
                        <span><i class="fa-solid fa-location-dot"></i> ${item.location || ''}</span>
                    </div>
                `;
                container.appendChild(card);
            });
        }
    } catch (e) {
        console.error("Falha ao carregar grid de eventos:", e);
    }
}

// ── Videos Grid Loader ──
async function loadVideosGrid() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/videos`);
        if (response.ok) {
            const data = await response.json();
            const container = document.getElementById("videos-grid-container");
            container.innerHTML = "";
            
            data.forEach((item, index) => {
                const card = document.createElement("div");
                card.className = "video-card glass-panel hover-grow animate-fade-in";
                card.style.animationDelay = `${index * 0.05}s`;
                card.innerHTML = `
                    <div class="video-thumb-placeholder">
                        <div class="video-thumb-play btn-view-transcription" data-id="${item.id}"><i class="fa-solid fa-play"></i></div>
                    </div>
                    <h4 class="item-title">${item.title}</h4>
                    <p class="item-desc">${item.summary || ''}</p>
                    <div class="card-footer-info" style="border:none; padding-top:0;">
                        <span><i class="fa-solid fa-clock"></i> ${item.duration || '45m'}</span>
                        <button class="btn-secondary btn-view-transcription" data-id="${item.id}">Ver Transcrição</button>
                    </div>
                `;
                container.appendChild(card);
            });
            
            bindVideoTriggers();
        }
    } catch (e) {
        console.error("Falha ao carregar grid de vídeos:", e);
    }
}

// ── News Grid Loader ──
async function loadNewsGrid() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/news`);
        if (response.ok) {
            const data = await response.json();
            const container = document.getElementById("news-grid-container");
            container.innerHTML = "";
            
            data.forEach((item, index) => {
                const card = document.createElement("div");
                card.className = "item-card glass-panel hover-grow animate-fade-in";
                card.style.animationDelay = `${index * 0.05}s`;
                card.innerHTML = `
                    <span class="badge-gold">NOTÍCIA / IMPRENSA</span>
                    <h4 class="item-title">${item.title}</h4>
                    <p class="item-desc">${item.summary || ''}</p>
                    <div class="card-footer-info">
                        <span><i class="fa-solid fa-newspaper"></i> ${item.publisher || ''}</span>
                        <span><i class="fa-solid fa-calendar"></i> ${item.date || ''}</span>
                    </div>
                `;
                container.appendChild(card);
            });
        }
    } catch (e) {
        console.error("Falha ao carregar grid de notícias:", e);
    }
}

// ── Testimonials Section Loader ──
async function loadTestimonialsSection() {
    try {
        const studentsResp = await fetch(`${API_BASE_URL}/api/students`);
        if (studentsResp.ok) {
            const data = await studentsResp.json();
            const container = document.getElementById("students-list-view");
            container.innerHTML = "";
            
            data.forEach(item => {
                const itemDiv = document.createElement("div");
                itemDiv.className = "student-item";
                itemDiv.innerHTML = `
                    <div class="student-avatar"><i class="fa-solid fa-user-graduate"></i></div>
                    <div class="student-meta">
                        <span class="student-name">${item.name}</span>
                        <span class="student-course">Harmonização Avançada</span>
                    </div>
                `;
                container.appendChild(itemDiv);
            });
        }
        
        const testimonialsResp = await fetch(`${API_BASE_URL}/api/testimonials`);
        if (testimonialsResp.ok) {
            const data = await testimonialsResp.json();
            const container = document.getElementById("testimonials-list-view");
            container.innerHTML = "";
            
            data.forEach(item => {
                const itemDiv = document.createElement("div");
                itemDiv.className = "testimonial-card-item";
                itemDiv.innerHTML = `
                    <p>"${item.content}"</p>
                    <div class="testimonial-card-author">${item.author} (${translateRelation(item.relation)})</div>
                `;
                container.appendChild(itemDiv);
            });
        }
    } catch (e) {
        console.error("Falha ao carregar seção de depoimentos:", e);
    }
}

// ── Sources Table Loader ──
async function loadSourcesTable() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/sources`);
        if (response.ok) {
            const data = await response.json();
            const body = document.getElementById("sources-table-body");
            body.innerHTML = "";
            
            data.forEach(item => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td><strong>${item.title}</strong></td>
                    <td><span class="badge-gold" style="font-size:10px; margin:0;">${item.type.toUpperCase()}</span></td>
                    <td><a href="${item.url}" target="_blank" class="timeline-link">${item.url} <i class="fa-solid fa-arrow-up-right-from-square"></i></a></td>
                    <td>${new Date(item.capture_date).toLocaleDateString('pt-BR')}</td>
                `;
                body.appendChild(row);
            });
        }
    } catch (e) {
        console.error("Falha ao carregar tabela de fontes:", e);
    }
}

// ── Dynamic Video Modal Open ──
async function openTranscriptionModal(videoId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/videos`);
        if (response.ok) {
            const list = await response.json();
            const video = list.find(v => v.id == videoId);
            if (video) {
                document.getElementById("transcription-modal-title").textContent = video.title;
                document.getElementById("transcription-modal-summary").textContent = video.summary;
                document.getElementById("transcription-modal-text").textContent = video.transcription;
                
                modal.classList.add("active");
            }
        }
    } catch (e) {
        console.error("Erro ao carregar transcrição do vídeo:", e);
    }
}

function initModalClose() {
    btnCloseModal.addEventListener("click", () => {
        modal.classList.remove("active");
    });
    
    modal.addEventListener("click", (e) => {
        if (e.target === modal) {
            modal.classList.remove("active");
        }
    });
}

function bindVideoTriggers() {
    const triggers = document.querySelectorAll(".btn-view-transcription");
    triggers.forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();
            const id = btn.getAttribute("data-id");
            openTranscriptionModal(id);
        });
    });
}

// ── Synchronization Pipeline Actions ──
function initSyncButton() {
    btnSyncPipeline.addEventListener("click", () => {
        btnSyncPipeline.disabled = true;
        btnSyncPipeline.querySelector("i").classList.add("fa-spin");
        btnSyncPipeline.querySelector("span:last-child").textContent = "Sincronizando V2...";
        
        setTimeout(async () => {
            btnSyncPipeline.disabled = false;
            btnSyncPipeline.querySelector("i").classList.remove("fa-spin");
            btnSyncPipeline.querySelector("span:last-child").textContent = "Buscar Atualizações";
            
            await loadProfile();
            await loadRelevanceMetrics();
            await loadTimelineData();
            
            showToast("Banco de Dados Biográfico Sincronizado com Sucesso V2!");
        }, 1500);
    });
}

function showToast(message) {
    const toast = document.getElementById("toast-notif");
    const toastText = document.getElementById("toast-message-text");
    toastText.textContent = message;
    
    toast.classList.add("active");
    
    setTimeout(() => {
        toast.classList.remove("active");
    }, 4000);
}

// ── Global Search Filter ──
function initSearch() {
    searchInput.addEventListener("input", () => {
        const query = searchInput.value.toLowerCase().trim();
        
        if (currentSection === "timeline") {
            const cards = document.querySelectorAll(".timeline-item-card");
            cards.forEach(card => {
                const text = card.textContent.toLowerCase();
                card.style.display = text.includes(query) ? "block" : "none";
            });
        }
        else if (currentSection === "courses" || currentSection === "events" || currentSection === "videos" || currentSection === "news") {
            const cards = document.querySelectorAll(".item-card, .video-card");
            cards.forEach(card => {
                const text = card.textContent.toLowerCase();
                card.style.display = text.includes(query) ? "flex" : "none";
            });
        }
    });
}

// ── Utility Functions ──

function animateValue(id, start, end, duration) {
    const obj = document.getElementById(id);
    if (!obj) return;
    
    if (start === end) {
        obj.textContent = end;
        return;
    }
    
    const range = end - start;
    let current = start;
    const increment = end > start ? 1 : -1;
    const stepTime = Math.abs(Math.floor(duration / range));
    
    const timer = setInterval(() => {
        current += increment;
        obj.textContent = current;
        if (current === end) {
            clearInterval(timer);
        }
    }, Math.max(stepTime, 20));
}

function initTestimonialRotation() {
    const slides = document.querySelectorAll(".testimonial-slide");
    let currentSlide = 0;
    
    if (slides.length <= 1) return;
    
    setInterval(() => {
        slides[currentSlide].classList.remove("active");
        currentSlide = (currentSlide + 1) % slides.length;
        slides[currentSlide].classList.add("active");
    }, 5000);
}

function translateType(type) {
    const map = {
        "course": "Curso",
        "event": "Evento",
        "award": "Prêmio",
        "video": "Vídeo",
        "news": "Imprensa",
        "social": "Redes Sociais"
    };
    return map[type] || type.toUpperCase();
}

function translateRelation(rel) {
    const map = {
        "student": "Aluno Mentorado",
        "patient": "Paciente",
        "partner": "Parceiro"
    };
    return map[rel] || rel;
}

function getMonthName(monthNum) {
    const months = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ];
    return months[parseInt(monthNum) - 1] || "Dezembro";
}
