// ── Front-End Application Controller V2 ──

const API_BASE_URL = (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
    ? "http://127.0.0.1:8000"
    : "https://macdonalts.agenciacyborg.com";


// SPA & Timeline State Management
let timelineData = [];
let relevanceData = {};
let currentSection = "overview";
let displayMode = "standard"; // "standard" or "hierarchical"
let sourcesMap = {}; // Global map linking source_id -> Source object

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
document.addEventListener("DOMContentLoaded", async () => {
    initNavigation();
    await loadSourcesMap();
    loadProfile();
    loadRelevanceMetrics();
    loadDashboardTestimonials();
    loadTimelineData();
    initSyncButton();
    initRunSearchButton();
    initSearch();
    initModalClose();
    initTimelineModeButtons();
    initClearFiltersButton();
    initPresenceMap();
    initMatrixRain();
    initPrintTimelineButton();
    initPrintLattesButton();
    initSearchConfig();
    loadSearchConfig();
    initEditItemModal();
    initSectionSummaries();
});

async function loadSourcesMap() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/sources`);
        if (response.ok) {
            const data = await response.json();
            data.forEach(src => {
                sourcesMap[src.id] = src;
            });
        }
    } catch (e) {
        console.error("Erro ao carregar mapa de fontes:", e);
    }
}

function initPrintTimelineButton() {
    const btnPrint = document.getElementById("btn-print-timeline");
    if (btnPrint) {
        btnPrint.addEventListener("click", () => {
            window.print();
        });
    }
}

function initPrintLattesButton() {
    const btnPrint = document.getElementById("btn-print-lattes");
    if (btnPrint) {
        btnPrint.addEventListener("click", () => {
            document.body.classList.add("printing-lattes");
            window.print();
            setTimeout(() => {
                document.body.classList.remove("printing-lattes");
            }, 1000);
        });
    }
}

// ── Matrix Rain Visual Engine ──
let matrixInterval = null;
function initMatrixRain() {
    const canvas = document.getElementById("matrix-canvas");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    
    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;
    
    const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$#@%&*()_+{}[]|:;<>,.?/~";
    const fontSize = 14;
    let columns = Math.floor(width / fontSize);
    
    const drops = [];
    for (let i = 0; i < columns; i++) {
        drops[i] = Math.random() * -100; // Start offscreen staggered
    }
    
    function draw() {
        const isLight = document.body.classList.contains("light-theme");
        
        // Trail opacity
        ctx.fillStyle = isLight ? "rgba(245, 245, 247, 0.08)" : "rgba(7, 7, 9, 0.08)";
        ctx.fillRect(0, 0, width, height);
        
        ctx.font = `bold ${fontSize}px monospace`;
        
        for (let i = 0; i < drops.length; i++) {
            const char = chars[Math.floor(Math.random() * chars.length)];
            
            // Highlight the leading character or tips of the rain
            if (drops[i] * fontSize > height - 100) {
                ctx.fillStyle = isLight ? "#aa00ff" : "#00f3ff";
            } else {
                ctx.fillStyle = isLight ? "#00f3ff" : "#aa00ff";
            }
            
            ctx.fillText(char, i * fontSize, drops[i] * fontSize);
            
            if (drops[i] * fontSize > height && Math.random() > 0.98) {
                drops[i] = 0;
            }
            drops[i]++;
        }
    }
    
    // Window Resize Handler
    window.addEventListener("resize", () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
        const newCols = Math.floor(width / fontSize);
        if (newCols > drops.length) {
            for (let i = drops.length; i < newCols; i++) {
                drops[i] = Math.random() * -100;
            }
        }
    });
    
    if (matrixInterval) clearInterval(matrixInterval);
    matrixInterval = setInterval(draw, 33);
}



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
        "search-config": "Parâmetros de Busca & Monitoramento",
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
    if (sectionId === "search-config") loadSearchConfig();
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
    // Use event delegation on the buttons container for reliability
    const buttonsContainer = document.querySelector(".display-mode-buttons");
    if (!buttonsContainer) return;

    buttonsContainer.addEventListener("click", (e) => {
        const btn = e.target.closest(".display-mode-btn");
        if (!btn) return;

        // Update active state on all buttons
        buttonsContainer.querySelectorAll(".display-mode-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");

        // Set the mode
        if (btn.id === "btn-mode-standard") {
            displayMode = "standard";
        } else if (btn.id === "btn-mode-hierarchical") {
            displayMode = "hierarchical";
        }

        // Re-render with new mode
        renderTimelineView();
    });
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
    const timelineLine = activeTimelineSection ? activeTimelineSection.querySelector(".timeline-line") : null;

    if (activeTimelineSection) {
        if (displayMode === "hierarchical") {
            activeTimelineSection.classList.remove("timeline-container");
            activeTimelineSection.classList.add("timeline-hierarchical");
            if (timelineLine) timelineLine.style.display = "none";
        } else {
            activeTimelineSection.classList.add("timeline-container");
            activeTimelineSection.classList.remove("timeline-hierarchical");
            if (timelineLine) timelineLine.style.display = "";
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
            let data = await response.json();

            // Handle presence map location filtering client-side
            const filterInfo = document.getElementById("lattes-filter-info");
            const filterCity = document.getElementById("lattes-filter-city");
            const btnClear = document.getElementById("btn-clear-lattes-filter");

            if (selectedLocation) {
                if (filterInfo) filterInfo.style.display = "flex";
                if (filterCity) filterCity.textContent = selectedLocation;

                // Filter lists inside data by selectedLocation
                const filterFunc = item => !selectedLocation || item.location === selectedLocation;
                data.formacao = data.formacao.filter(filterFunc);
                data.atuacao = data.atuacao.filter(filterFunc);
                data.producoes = data.producoes.filter(filterFunc);
                data.eventos = data.eventos.filter(filterFunc);
                data.cursos = data.cursos.filter(filterFunc);
                data.orientacoes = data.orientacoes.filter(filterFunc);
                data.certificacoes = data.certificacoes.filter(filterFunc);
            } else {
                if (filterInfo) filterInfo.style.display = "none";
            }

            if (btnClear && !btnClear.dataset.bound) {
                btnClear.dataset.bound = "true";
                btnClear.addEventListener("click", () => {
                    selectedLocation = null;
                    loadLattesCurriculum();
                });
            }

            // Populate Lattes sections
            populateLattesSection("lattes-content-formacao", data.formacao, "Nenhuma formação registrada para esta localidade.");
            populateLattesSection("lattes-content-atuacao", data.atuacao, "Nenhuma atuação profissional registrada para esta localidade.");
            populateLattesSection("lattes-content-producoes", data.producoes, "Nenhuma produção registrada para esta localidade.");
            populateLattesSection("lattes-content-eventos", data.eventos, "Nenhum evento registrado para esta localidade.");
            populateLattesSection("lattes-content-cursos", data.cursos, "Nenhum curso registrado para esta localidade.");
            populateLattesSection("lattes-content-orientacoes", data.orientacoes, "Nenhuma orientação registrada para esta localidade.");
            populateLattesSection("lattes-content-certificacoes", data.certificacoes, "Nenhuma certificação registrada para esta localidade.");
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
        div.style.display = "flex";
        div.style.justifyContent = "space-between";
        div.style.alignItems = "flex-start";
        div.style.gap = "15px";
        div.style.padding = "10px 0";
        div.style.borderBottom = "1px solid rgba(255, 255, 255, 0.05)";

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
            <div style="flex: 1;">
                <span class="lattes-item-year">${item.year} - ${item.month ? `${item.month.toString().padStart(2, '0')}/` : ''}${item.year}</span>
                <span><strong>${item.title}</strong>. ${item.description || ''}${details}.</span>
            </div>
            <button class="lattes-edit-btn" data-id="${item.id}" style="flex-shrink: 0;">
                <i class="fa-solid fa-pen"></i> Editar
            </button>
        `;

        div.querySelector('.lattes-edit-btn').addEventListener('click', () => {
            openEditItemModal(item);
        });

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
        card.style.cursor = "pointer";
        card.innerHTML = `
            <div class="geo-card-header">
                <span class="geo-card-title">${c.city} - ${c.state}</span>
                <span class="geo-card-stat">${c.itemsCount} ${c.itemsCount === 1 ? 'Registro' : 'Registros'}</span>
            </div>
            <div class="geo-card-detail" style="margin-bottom: 8px;">
                ${c.details.slice(0, 3).map(d => `• ${d}`).join('<br>')}
                ${c.details.length > 3 ? `<br>• e mais ${c.details.length - 3} registros...` : ''}
            </div>
            <span class="timeline-link" style="font-size: 11px; display: inline-flex; align-items: center; gap: 4px; pointer-events: none;"><i class="fa-solid fa-circle-info"></i> Explorar Fontes no Eixo Cronológico</span>
        `;

        // Setup marker highlights on card hover
        card.addEventListener("mouseenter", () => {
            highlightMarker(c.city.toLowerCase());
        });

        // Click handler to route and filter timeline dynamically
        card.addEventListener("click", () => {
            selectedLocation = `${c.city}/${c.state}`;
            const navTimelineBtn = document.getElementById("btn-nav-timeline");
            if (navTimelineBtn) {
                navTimelineBtn.click();
            }
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
                card.style.cursor = "pointer";
                
                const src = sourcesMap[item.source_id];
                const sourceHtml = src ? `<a href="${src.url}" target="_blank" class="timeline-link" style="margin-top: 10px; display: inline-flex; align-items: center; gap: 6px; font-size: 11px;"><i class="fa-solid fa-arrow-up-right-from-square"></i> Abrir Fonte Original</a>` : "";

                card.innerHTML = `
                    <span class="badge-gold">${item.role === 'instructor' ? 'CURSO MINISTRADO' : 'REALIZADO'}</span>
                    <h4 class="item-title">${item.title}</h4>
                    <p class="item-desc">${item.description || ''}</p>
                    <div class="card-footer-info" style="margin-bottom: 4px;">
                        <span><i class="fa-solid fa-calendar"></i> ${item.date || ''}</span>
                        <span><i class="fa-solid fa-location-dot"></i> ${item.location || ''}</span>
                    </div>
                    ${sourceHtml}
                `;

                // Toggle source button on card click
                card.addEventListener("click", (e) => {
                    if (e.target.closest("a") || e.target.closest("button")) return;
                    card.classList.toggle("focused-card");
                });

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
                card.style.cursor = "pointer";
                
                const src = sourcesMap[item.source_id];
                const sourceHtml = src ? `<a href="${src.url}" target="_blank" class="timeline-link" style="margin-top: 10px; display: inline-flex; align-items: center; gap: 6px; font-size: 11px;"><i class="fa-solid fa-arrow-up-right-from-square"></i> Abrir Fonte Original</a>` : "";

                card.innerHTML = `
                    <span class="badge-gold">CONGRESSO / WORKSHOP</span>
                    <h4 class="item-title">${item.name}</h4>
                    <p class="item-desc">${item.description || ''}</p>
                    <div class="card-footer-info" style="margin-bottom: 4px;">
                        <span><i class="fa-solid fa-calendar"></i> ${item.date || ''}</span>
                        <span><i class="fa-solid fa-location-dot"></i> ${item.location || ''}</span>
                    </div>
                    ${sourceHtml}
                `;

                // Toggle source button on card click
                card.addEventListener("click", (e) => {
                    if (e.target.closest("a") || e.target.closest("button")) return;
                    card.classList.toggle("focused-card");
                });

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
                card.style.cursor = "pointer";
                
                const srcHtml = item.url ? `<a href="${item.url}" target="_blank" class="timeline-link" style="margin-top: 10px; display: inline-flex; align-items: center; gap: 6px; font-size: 11px;"><i class="fa-solid fa-arrow-up-right-from-square"></i> Ver Canal Original</a>` : "";

                card.innerHTML = `
                    <div class="video-thumb-placeholder">
                        <div class="video-thumb-play btn-view-transcription" data-id="${item.id}"><i class="fa-solid fa-play"></i></div>
                    </div>
                    <h4 class="item-title">${item.title}</h4>
                    <p class="item-desc">${item.summary || ''}</p>
                    <div class="card-footer-info" style="border:none; padding-top:0; margin-bottom: 4px;">
                        <span><i class="fa-solid fa-clock"></i> ${item.duration || '45m'}</span>
                        <button class="btn-secondary btn-view-transcription" data-id="${item.id}">Ver Transcrição</button>
                    </div>
                    ${srcHtml}
                `;

                // Toggle source button on card click
                card.addEventListener("click", (e) => {
                    if (e.target.closest("a") || e.target.closest("button") || e.target.closest(".video-thumb-play")) return;
                    card.classList.toggle("focused-card");
                });

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
                card.style.cursor = "pointer";
                
                const newsUrl = item.url || (sourcesMap[item.source_id] ? sourcesMap[item.source_id].url : "");
                const sourceHtml = newsUrl ? `<a href="${newsUrl}" target="_blank" class="timeline-link" style="margin-top: 10px; display: inline-flex; align-items: center; gap: 6px; font-size: 11px;"><i class="fa-solid fa-arrow-up-right-from-square"></i> Abrir Notícia Completa</a>` : "";

                card.innerHTML = `
                    <span class="badge-gold">NOTÍCIA / IMPRENSA</span>
                    <h4 class="item-title">${item.title}</h4>
                    <p class="item-desc">${item.summary || ''}</p>
                    <div class="card-footer-info" style="margin-bottom: 4px;">
                        <span><i class="fa-solid fa-newspaper"></i> ${item.publisher || ''}</span>
                        <span><i class="fa-solid fa-calendar"></i> ${item.date || ''}</span>
                    </div>
                    ${sourceHtml}
                `;

                // Toggle source button on card click
                card.addEventListener("click", (e) => {
                    if (e.target.closest("a") || e.target.closest("button")) return;
                    card.classList.toggle("focused-card");
                });

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
                
                const src = sourcesMap[item.source_id];
                const sourceHtml = src ? `<a href="${src.url}" target="_blank" class="timeline-link" style="display: inline-flex; align-items: center; gap: 4px; font-size: 10px; margin-top: 4px;"><i class="fa-solid fa-arrow-up-right-from-square"></i> Ver Fonte</a>` : "";

                itemDiv.innerHTML = `
                    <div class="student-avatar"><i class="fa-solid fa-user-graduate"></i></div>
                    <div class="student-meta">
                        <span class="student-name">${item.name}</span>
                        <span class="student-course">Harmonização Avançada</span>
                        ${sourceHtml}
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
                
                const src = sourcesMap[item.source_id];
                const sourceHtml = src ? `<a href="${src.url}" target="_blank" class="timeline-link" style="display: inline-flex; align-items: center; gap: 4px; font-size: 10px; margin-top: 6px; float: left;"><i class="fa-solid fa-arrow-up-right-from-square"></i> Ver Fonte</a>` : "";

                itemDiv.innerHTML = `
                    <p>"${item.content}"</p>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
                        ${sourceHtml}
                        <div class="testimonial-card-author" style="margin: 0; width: auto;">${item.author} (${translateRelation(item.relation)})</div>
                    </div>
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

// YouTube URL extractor utility
function getYouTubeEmbedUrl(url) {
    if (!url) return null;
    let videoId = null;
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
    const match = url.match(regExp);
    if (match && match[2].length === 11) {
        videoId = match[2];
    }
    return videoId ? `https://www.youtube.com/embed/${videoId}` : null;
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

                // Load YouTube embed player
                const embedUrl = getYouTubeEmbedUrl(video.url);
                const playerContainer = document.getElementById("modal-video-player-container");
                if (embedUrl) {
                    playerContainer.innerHTML = `<iframe width="100%" height="340" src="${embedUrl}?autoplay=1" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen style="display: block; border: none;"></iframe>`;
                    playerContainer.style.display = "block";
                } else {
                    playerContainer.innerHTML = "";
                    playerContainer.style.display = "none";
                }

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
        document.getElementById("modal-video-player-container").innerHTML = ""; // Stop video playback
    });

    modal.addEventListener("click", (e) => {
        if (e.target === modal) {
            modal.classList.remove("active");
            document.getElementById("modal-video-player-container").innerHTML = ""; // Stop video playback
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
    const btn = document.getElementById("btn-sync-pipeline");
    if (!btn) return;
    btn.addEventListener("click", () => {
        btn.disabled = true;
        btn.querySelector("i").classList.add("fa-spin");
        btn.querySelector("span").textContent = "Sincronizando...";

        setTimeout(async () => {
            btn.disabled = false;
            btn.querySelector("i").classList.remove("fa-spin");
            btn.querySelector("span").textContent = "Buscar Atualizações";

            await loadProfile();
            await loadRelevanceMetrics();
            await loadTimelineData();

            showToast("Banco de Dados Sincronizado com Sucesso!");
        }, 1500);
    });
}

function initRunSearchButton() {
    const btn = document.getElementById("btn-run-search");
    if (!btn) return;
    btn.addEventListener("click", async () => {
        btn.disabled = true;
        btn.querySelector("i").classList.add("fa-spin");
        btn.querySelector("span").textContent = "Executando Varredura...";

        try {
            const resp = await fetch(`${API_BASE_URL}/api/pipeline/run`, { method: "POST" });
            const msg = resp.ok ? "Varredura iniciada! Os resultados serão atualizados em breve." : "Pipeline iniciado (modo simulado).";
            showToast(msg);
        } catch (e) {
            showToast("Pipeline iniciado em modo simulado. Nenhum agente conectado.");
        } finally {
            setTimeout(() => {
                btn.disabled = false;
                btn.querySelector("i").classList.remove("fa-spin");
                btn.querySelector("span").textContent = "Rodar Busca Agora";
            }, 2500);
        }
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

// ══════════════════════════════════════════════════════════════════════
// SEARCH CONFIG MODULE  (Parâmetros de Busca)
// ══════════════════════════════════════════════════════════════════════

let searchConfigData = { keywords: [], sites: [], engines: [], socials: [] };

const TYPE_ICONS = {
    keyword: 'fa-key',
    site: 'fa-globe',
    engine: 'fa-magnifying-glass',
    social: 'fa-share-nodes'
};

function initSearchConfig() {
    // Tab switching
    const tabs = document.querySelectorAll('.sconfig-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const target = tab.getAttribute('data-tab');
            document.querySelectorAll('.sconfig-panel').forEach(p => p.classList.remove('active'));
            const panel = document.getElementById(`sconfig-panel-${target}`);
            if (panel) panel.classList.add('active');
        });
    });

    // Add button
    const btnAdd = document.getElementById('btn-add-search-param');
    if (btnAdd) {
        btnAdd.addEventListener('click', addSearchParam);
    }

    // Enter key on inputs
    ['sconfig-value-input', 'sconfig-label-input', 'sconfig-notes-input'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('keydown', e => { if (e.key === 'Enter') addSearchParam(); });
    });
}

async function loadSearchConfig() {
    try {
        const resp = await fetch(`${API_BASE_URL}/api/search-params`);
        if (!resp.ok) throw new Error('API error');
        const data = await resp.json();

        // If API returns empty arrays, seed with defaults
        const hasData = (data.keywords && data.keywords.length > 0) ||
                        (data.sites && data.sites.length > 0) ||
                        (data.engines && data.engines.length > 0) ||
                        (data.socials && data.socials.length > 0);

        if (hasData) {
            searchConfigData = data;
        } else {
            searchConfigData = getDefaultSearchParams();
        }
    } catch (e) {
        // API offline — seed with defaults
        searchConfigData = getDefaultSearchParams();
        console.warn('Usando parâmetros padrão (API offline):', e);
    }

    renderSearchConfigPanel('keywords');
    renderSearchConfigPanel('sites');
    renderSearchConfigPanel('engines');
    renderSearchConfigPanel('socials');
}

function getDefaultSearchParams() {
    return {
        keywords: [
            { id: -1, type: 'keyword', value: 'Nássara Mesquita', label: 'Nome principal', active: true, notes: 'Variação mais comum nas buscas' },
            { id: -2, type: 'keyword', value: 'Nássara Borges Mesquita Oliveira', label: 'Nome completo', active: true, notes: 'Conforme registrado no Currículo Lattes' },
            { id: -3, type: 'keyword', value: 'OLIVEIRA, N. B. M.', label: 'Citação bibliográfica', active: true, notes: 'Formato de citação em produções científicas' },
            { id: -4, type: 'keyword', value: 'Dra. Nássara Mesquita', label: 'Nome profissional', active: true, notes: 'Formato usado em mídias e palestras' },
            { id: -5, type: 'keyword', value: 'Nassara Mesquita Microtox', label: 'Técnica Microtox', active: true, notes: 'Associação de marca/técnica profissional' },
            { id: -6, type: 'keyword', value: 'Nassara Mesquita harmonização facial', label: 'Especialidade principal', active: true, notes: 'Foco de atuação clínica' },
            { id: -7, type: 'keyword', value: 'Mipps + HRF Facial Trainning', label: 'Curso internacional', active: true, notes: 'Curso de anatomia aplicada facial nos EUA' },
            { id: -8, type: 'keyword', value: 'Summer Peel', label: 'Método estético', active: true, notes: 'Método de peeling químico e revitalização' },
            { id: -9, type: 'keyword', value: 'Striort', label: 'Tratamento ortomolecular', active: true, notes: 'Técnica ortomolecular de combate a estrias' },
            { id: -90, type: 'keyword', value: 'Flaci 10', label: 'Protocolo de flacidez', active: true, notes: 'Técnica Flaci 10 de tratamento corporal' },
            { id: -91, type: 'keyword', value: 'Lipoescultura Gessada', label: 'Técnica corporal', active: true, notes: 'Tratamento ortomolecular para gordura localizada' }
        ],
        sites: [
            { id: -10, type: 'site', value: 'lattes.cnpq.br/7120531705115048', label: 'Currículo Lattes', active: true, notes: 'Perfil oficial do CNPq' },
            { id: -11, type: 'site', value: 'instagram.com/nassaramesquita', label: 'Instagram Oficial', active: true, notes: 'Principal canal de engajamento' },
            { id: -12, type: 'site', value: 'escavador.com', label: 'Escavador', active: true, notes: 'Indexador acadêmico público' },
            { id: -13, type: 'site', value: 'crfgo.org.br', label: 'CRF-GO', active: true, notes: 'Conselho Regional de Farmácia de Goiás' },
            { id: -14, type: 'site', value: 'revistas.unilus.edu.br', label: 'Revista UNILUS', active: true, notes: 'Periódico do artigo de Fototerapia publicado em 2019' },
            { id: -15, type: 'site', value: 'iepg.edu.br', label: 'IEPG', active: true, notes: 'Instituto de pós-graduação onde é coordenadora' },
            { id: -16, type: 'site', value: 'cff.org.br', label: 'CFF', active: true, notes: 'Conselho Federal de Farmácia - GT Estética' },
            { id: -17, type: 'site', value: 'faculdadecathedral.edu.br', label: 'Faculdades Cathedral', active: true, notes: 'Instituição onde orientou 17 monografias' }
        ],
        engines: [
            { id: -20, type: 'engine', value: 'Google Search', label: 'Google', active: true, notes: 'Principal motor de busca global' },
            { id: -21, type: 'engine', value: 'Google Scholar', label: 'Google Acadêmico', active: true, notes: 'Pesquisa de publicações e citações científicas' },
            { id: -22, type: 'engine', value: 'YouTube Search', label: 'YouTube', active: true, notes: 'Pesquisa de vídeos e podcasts' },
            { id: -23, type: 'engine', value: 'Bing', label: 'Bing', active: false, notes: 'Motor de busca secundário' }
        ],
        socials: [
            { id: -30, type: 'social', value: 'instagram.com/dranassaramesquita', label: 'Instagram Profissional', active: true, notes: 'Perfil oficial da Dra. Nássara Mesquita no Instagram' },
            { id: -31, type: 'social', value: 'facebook.com/dranassaramesquita', label: 'Facebook Profissional', active: true, notes: 'Perfil no Facebook' },
            { id: -32, type: 'social', value: 'linkedin.com/in/nassara-mesquita-878880182', label: 'LinkedIn Acadêmico', active: true, notes: 'Perfil acadêmico e profissional no LinkedIn' }
        ]
    };
}

function renderSearchConfigPanel(type) {
    const listEl = document.getElementById(`sconfig-${type}-list`);
    const countEl = document.getElementById(`count-${type}`);
    if (!listEl) return;

    const items = searchConfigData[type] || [];
    const activeCount = items.filter(i => i.active).length;

    if (countEl) countEl.textContent = `${activeCount} ativo${activeCount !== 1 ? 's' : ''}`;

    if (items.length === 0) {
        let emptyIcon = 'circle-info';
        if (type === 'keywords') emptyIcon = 'key';
        else if (type === 'sites') emptyIcon = 'globe';
        else if (type === 'engines') emptyIcon = 'magnifying-glass';
        else if (type === 'socials') emptyIcon = 'share-nodes';

        listEl.innerHTML = `<div class="sconfig-empty" style="text-align: center; padding: 30px; color: var(--text-muted); font-size: 13px;"><i class="fa-solid fa-${emptyIcon}" style="display: block; font-size: 24px; margin-bottom: 10px; color: var(--cyan);"></i>Nenhum parâmetro cadastrado.</div>`;
        return;
    }

    listEl.innerHTML = '';
    items.forEach(item => {
        const singularType = type === 'keywords' ? 'keyword' : type === 'sites' ? 'site' : type === 'engines' ? 'engine' : 'social';
        const icon = TYPE_ICONS[singularType] || 'circle';
        const div = document.createElement('div');
        div.className = `sconfig-item${item.active ? '' : ' inactive'}`;
        div.setAttribute('data-id', item.id);
        div.innerHTML = `
            <div class="sconfig-item-icon"><i class="fa-solid fa-${icon}"></i></div>
            <div class="sconfig-item-body">
                <div class="sconfig-item-value">${item.value}</div>
                <div class="sconfig-item-label">${item.label || ''}</div>
                ${item.notes ? `<div class="sconfig-item-notes">${item.notes}</div>` : ''}
            </div>
            <div class="sconfig-item-actions">
                <button class="sconfig-btn toggle-btn ${item.active ? 'active-state' : ''}" data-id="${item.id}" data-type="${type}" data-active="${item.active ? 1 : 0}" title="${item.active ? 'Desativar' : 'Ativar'}">
                    <i class="fa-solid fa-${item.active ? 'eye' : 'eye-slash'}"></i>
                    ${item.active ? 'Ativo' : 'Inativo'}
                </button>
                <button class="sconfig-btn edit-param-btn" data-id="${item.id}" data-type="${type}" title="Editar">
                    <i class="fa-solid fa-pen"></i> Editar
                </button>
                <button class="sconfig-btn delete-btn" data-id="${item.id}" data-type="${type}" title="Remover">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </div>
        `;
        listEl.appendChild(div);
    });

    // Bind toggle buttons
    listEl.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const id = parseInt(btn.getAttribute('data-id'));
            const panelType = btn.getAttribute('data-type');
            const currentActive = parseInt(btn.getAttribute('data-active'));
            const newActive = currentActive === 1 ? 0 : 1;
            
            // Update local state
            const arr = searchConfigData[panelType];
            const idx = arr.findIndex(i => i.id === id);
            if (idx !== -1) arr[idx].active = newActive === 1;
            renderSearchConfigPanel(panelType);
            
            // Sync to API (if positive ID = real DB record)
            if (id > 0) {
                try {
                    await fetch(`${API_BASE_URL}/api/search-params/${id}?active=${newActive}`, { method: 'PUT' });
                } catch (e) { /* offline */ }
            }
            showToast(newActive ? 'Parâmetro ativado!' : 'Parâmetro desativado!');
        });
    });

    // Bind edit buttons
    listEl.querySelectorAll('.edit-param-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = parseInt(btn.getAttribute('data-id'));
            const panelType = btn.getAttribute('data-type');
            const item = searchConfigData[panelType].find(i => i.id === id);
            if (!item) return;

            const itemDiv = listEl.querySelector(`.sconfig-item[data-id="${id}"]`);
            if (!itemDiv) return;

            const bodyEl = itemDiv.querySelector('.sconfig-item-body');
            const actionsEl = itemDiv.querySelector('.sconfig-item-actions');

            // Replace body with edit inputs
            bodyEl.innerHTML = `
                <input type="text" class="edit-value-input" value="${item.value}" style="background:rgba(7,7,9,0.7); border:1px solid var(--cyan); color:#fff; border-radius:4px; padding:6px; font-size:12.5px; margin-bottom:6px; width:100%; outline:none;">
                <input type="text" class="edit-label-input" placeholder="Rótulo" value="${item.label || ''}" style="background:rgba(7,7,9,0.7); border:1px solid var(--cyan); color:#fff; border-radius:4px; padding:6px; font-size:11px; margin-bottom:6px; width:100%; outline:none;">
                <input type="text" class="edit-notes-input" placeholder="Observações" value="${item.notes || ''}" style="background:rgba(7,7,9,0.7); border:1px solid var(--cyan); color:#fff; border-radius:4px; padding:6px; font-size:11px; width:100%; outline:none;">
            `;

            // Replace actions with Save/Cancel
            actionsEl.innerHTML = `
                <button class="sconfig-btn save-param-btn" data-id="${id}" data-type="${panelType}" style="background:var(--cyan); color:#000; font-weight:600; padding:6px 12px; border-radius:30px;">
                    <i class="fa-solid fa-floppy-disk"></i> Salvar
                </button>
                <button class="sconfig-btn cancel-param-btn" data-id="${id}" data-type="${panelType}" style="background:rgba(255,255,255,0.05); color:#fff; padding:6px 12px; border-radius:30px;">
                    <i class="fa-solid fa-xmark"></i> Cancelar
                </button>
            `;

            // Bind save button
            actionsEl.querySelector('.save-param-btn').addEventListener('click', async () => {
                const newValue = bodyEl.querySelector('.edit-value-input').value.trim();
                const newLabel = bodyEl.querySelector('.edit-label-input').value.trim();
                const newNotes = bodyEl.querySelector('.edit-notes-input').value.trim();

                if (!newValue) {
                    showToast('O valor não pode ser vazio!');
                    return;
                }

                item.value = newValue;
                item.label = newLabel || newValue;
                item.notes = newNotes;

                renderSearchConfigPanel(panelType);

                // Sync with API
                if (id > 0) {
                    try {
                        const url = `${API_BASE_URL}/api/search-params/${id}?value=${encodeURIComponent(newValue)}&label=${encodeURIComponent(item.label)}&notes=${encodeURIComponent(newNotes)}`;
                        await fetch(url, { method: 'PUT' });
                        showToast('Parâmetro atualizado!');
                    } catch (e) {
                        showToast('Erro ao sincronizar com a API (modo offline).');
                    }
                } else {
                    showToast('Parâmetro atualizado localmente!');
                }
            });

            // Bind cancel button
            actionsEl.querySelector('.cancel-param-btn').addEventListener('click', () => {
                renderSearchConfigPanel(panelType);
            });
        });
    });

    // Bind delete buttons
    listEl.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const id = parseInt(btn.getAttribute('data-id'));
            const panelType = btn.getAttribute('data-type');
            
            searchConfigData[panelType] = searchConfigData[panelType].filter(i => i.id !== id);
            renderSearchConfigPanel(panelType);
            
            if (id > 0) {
                try {
                    await fetch(`${API_BASE_URL}/api/search-params/${id}`, { method: 'DELETE' });
                } catch (e) { /* offline */ }
            }
            showToast('Parâmetro removido!');
        });
    });
}

async function addSearchParam() {
    const typeEl = document.getElementById('sconfig-type-select');
    const valueEl = document.getElementById('sconfig-value-input');
    const labelEl = document.getElementById('sconfig-label-input');
    const notesEl = document.getElementById('sconfig-notes-input');

    const type = typeEl.value;
    const value = valueEl.value.trim();
    const label = labelEl.value.trim();
    const notes = notesEl.value.trim();

    if (!value) {
        showToast('Informe um valor para o parâmetro!');
        return;
    }

    const panelType = type === 'keyword' ? 'keywords' : type === 'site' ? 'sites' : type === 'engine' ? 'engines' : 'socials';
    const tempId = -(Date.now()); // negative temp ID

    const newItem = { id: tempId, type, value, label: label || value, active: true, notes };
    searchConfigData[panelType].push(newItem);
    renderSearchConfigPanel(panelType);

    // Clear form
    valueEl.value = '';
    labelEl.value = '';
    notesEl.value = '';

    // Activate the correct tab
    document.querySelectorAll('.sconfig-tab').forEach(t => {
        t.classList.toggle('active', t.getAttribute('data-tab') === panelType);
    });
    document.querySelectorAll('.sconfig-panel').forEach(p => {
        p.classList.toggle('active', p.id === `sconfig-panel-${panelType}`);
    });

    // Sync to API
    try {
        const url = `${API_BASE_URL}/api/search-params?type=${encodeURIComponent(type)}&value=${encodeURIComponent(value)}&label=${encodeURIComponent(label || value)}&notes=${encodeURIComponent(notes)}`;
        const resp = await fetch(url, { method: 'POST' });
        if (resp.ok) {
            const saved = await resp.json();
            // Replace temp ID with real DB ID
            const arr = searchConfigData[panelType];
            const idx = arr.findIndex(i => i.id === tempId);
            if (idx !== -1) arr[idx].id = saved.id;
            showToast('Parâmetro adicionado e sincronizado!');
        }
    } catch (e) {
        showToast('Parâmetro adicionado (modo offline).');
    }
}

// ── Translation & Date Helpers ──

function getMonthName(month) {
    const months = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ];
    const mIdx = parseInt(month) - 1;
    return months[mIdx] || "Dezembro";
}

function translateType(type) {
    const types = {
        "course": "Curso",
        "event": "Evento",
        "video": "Vídeo",
        "news": "Notícia",
        "award": "Prêmio",
        "lattes": "Currículo Lattes",
        "student": "Aluno",
        "testimonial": "Depoimento",
        "timeline": "Cronologia",
        "social": "Rede Social"
    };
    return types[type] || type;
}

function translateRelation(relation) {
    const relations = {
        "patient": "Paciente",
        "student": "Aluno/Mentorando",
        "peer": "Colega Profissional",
        "other": "Outro"
    };
    return relations[relation] || relation;
}

// ── Edit Lattes / Timeline Items ──
function openEditItemModal(item) {
    const modal = document.getElementById('edit-item-modal');
    if (!modal) return;

    document.getElementById('edit-item-id').value = item.id;
    document.getElementById('edit-item-title').value = item.title || "";
    document.getElementById('edit-item-description').value = item.description || "";
    document.getElementById('edit-item-year').value = item.year || "";
    document.getElementById('edit-item-date').value = item.date || "";
    document.getElementById('edit-item-participation').value = item.participation_type || "";
    document.getElementById('edit-item-category').value = item.category || "";

    modal.classList.add('active');
}

function initEditItemModal() {
    const modal = document.getElementById('edit-item-modal');
    const btnClose = document.getElementById('btn-close-edit-modal');
    const btnCancel = document.getElementById('btn-cancel-edit-modal');
    const form = document.getElementById('edit-item-form');

    if (!modal) return;

    const closeHandler = () => {
        modal.classList.remove('active');
    };

    if (btnClose) btnClose.addEventListener('click', closeHandler);
    if (btnCancel) btnCancel.addEventListener('click', closeHandler);

    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeHandler();
    });

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const id = document.getElementById('edit-item-id').value;
            const title = document.getElementById('edit-item-title').value;
            const description = document.getElementById('edit-item-description').value;
            const year = parseInt(document.getElementById('edit-item-year').value);
            const dateVal = document.getElementById('edit-item-date').value;
            const participation = document.getElementById('edit-item-participation').value;
            const categoryVal = document.getElementById('edit-item-category').value;

            try {
                const url = `${API_BASE_URL}/api/timeline/${id}?title=${encodeURIComponent(title)}&description=${encodeURIComponent(description)}&year=${year}&date=${encodeURIComponent(dateVal)}&participation_type=${encodeURIComponent(participation)}&category=${encodeURIComponent(categoryVal)}`;
                const response = await fetch(url, { method: 'PUT' });
                if (response.ok) {
                    showToast("Registro atualizado com sucesso!");
                    closeHandler();
                    await loadTimelineData();
                    await loadLattesCurriculum();
                } else {
                    showToast("Erro ao salvar alterações no servidor.");
                }
            } catch (err) {
                showToast("Erro ao se conectar ao servidor (modo offline).");
            }
        });
    }
}

// ── AI Section Summaries (Sobre) ──
const SECTIONS = ['courses', 'events', 'videos', 'news', 'testimonials'];

function initSectionSummaries() {
    SECTIONS.forEach(sec => {
        loadSectionSummary(sec);

        const btnEdit = document.getElementById(`btn-edit-summary-${sec}`);
        const btnCancel = document.getElementById(`btn-cancel-summary-${sec}`);
        const btnSave = document.getElementById(`btn-save-summary-${sec}`);
        const btnAi = document.getElementById(`btn-generate-summary-${sec}`);

        const form = document.getElementById(`edit-form-summary-${sec}`);
        const textEl = document.getElementById(`summary-text-${sec}`);
        const textarea = document.getElementById(`textarea-summary-${sec}`);

        if (btnEdit) {
            btnEdit.addEventListener('click', () => {
                textarea.value = textEl.textContent.trim().startsWith("Carregando resumo") ? "" : textEl.textContent.trim();
                form.style.display = 'block';
            });
        }

        if (btnCancel) {
            btnCancel.addEventListener('click', () => {
                form.style.display = 'none';
            });
        }

        if (btnSave) {
            btnSave.addEventListener('click', async () => {
                const newContent = textarea.value.trim();
                if (!newContent) {
                    showToast("O resumo não pode estar em branco!");
                    return;
                }

                btnSave.disabled = true;
                btnSave.textContent = "Salvando...";

                try {
                    const response = await fetch(`${API_BASE_URL}/api/section-summaries/${sec}?content=${encodeURIComponent(newContent)}`, { method: 'PUT' });
                    if (response.ok) {
                        textEl.textContent = newContent;
                        form.style.display = 'none';
                        showToast("Resumo atualizado com sucesso!");
                    } else {
                        showToast("Erro ao salvar resumo.");
                    }
                } catch (e) {
                    showToast("Erro ao se conectar (modo offline).");
                } finally {
                    btnSave.disabled = false;
                    btnSave.textContent = "Salvar";
                }
            });
        }

        if (btnAi) {
            btnAi.addEventListener('click', async () => {
                btnAi.disabled = true;
                const icon = btnAi.querySelector('i');
                if (icon) icon.className = "fa-solid fa-circle-notch fa-spin";
                textEl.classList.add('generating-ai');
                textEl.textContent = "Escrevendo e sintetizando biografia com Inteligência Artificial...";

                try {
                    const response = await fetch(`${API_BASE_URL}/api/section-summaries/${sec}/generate`, { method: 'POST' });
                    if (response.ok) {
                        const data = await response.json();
                        typeText(textEl, data.content);
                        showToast("Resumo gerado com IA e sincronizado!");
                    } else {
                        textEl.textContent = "Erro ao gerar resumo biográfico por IA.";
                        textEl.classList.remove('generating-ai');
                    }
                } catch (e) {
                    textEl.textContent = "Erro de conexão (modo offline).";
                    textEl.classList.remove('generating-ai');
                } finally {
                    btnAi.disabled = false;
                    if (icon) icon.className = "fa-solid fa-wand-magic-sparkles";
                }
            });
        }
    });
}

async function loadSectionSummary(sec) {
    const textEl = document.getElementById(`summary-text-${sec}`);
    if (!textEl) return;

    try {
        const response = await fetch(`${API_BASE_URL}/api/section-summaries/${sec}`);
        if (response.ok) {
            const data = await response.json();
            if (data.content) {
                textEl.textContent = data.content;
            } else {
                textEl.textContent = getSectionDefaultSummaryText(sec);
            }
        }
    } catch (e) {
        textEl.textContent = getSectionDefaultSummaryText(sec);
    }
}

function getSectionDefaultSummaryText(sec) {
    const defaults = {
        courses: "A Dra. Nássara Mesquita possui uma sólida trajetória de liderança e docência na área de saúde estética, tendo ministrado e participado de importantes cursos e mentorias profissionais de alto nível. É amplamente reconhecida como referência nacional e pioneira clínica pelo desenvolvimento do inovador método Microtox.",
        events: "Como palestrante de destaque nacional, a Dra. Nássara Mesquita atua ativamente em congressos científicos, seminários e simpósios em todo o Brasil. Sua presença constante em fóruns consolida sua autoridade clínica de ponta frente à farmácia estética.",
        videos: "A difusão do conhecimento estético e a educação profissional fazem parte da essência biográfica da Dra. Nássara Mesquita. Através de entrevistas de alta visibilidade nacional (como na TV Caras / IBTV) e podcasts de anatomia facial aplicada, ela educa milhares de profissionais.",
        news: "Com forte destaque na mídia especializada e conselhos de classe, a presença na imprensa da Dra. Nássara Mesquita valida a excelência de suas técnicas inovadoras. Suas publicações e entrevistas científicas na Revista do CRF abordam a regulamentação profissional.",
        testimonials: "Completando uma expressiva marca acadêmica, a Dra. Nássara Mesquita já orientou e supervisionou formalmente mais de 17 monografias e teses científicas de especialização em Saúde Estética e Cosmetologia. O carinho e a profunda gratidão de centenas de alunos mentorados e pacientes fiéis atestam sua maestria clínica."
    };
    return defaults[sec] || "";
}

function typeText(element, text) {
    element.classList.remove('generating-ai');
    element.textContent = "";
    let idx = 0;
    const interval = setInterval(() => {
        element.textContent += text[idx];
        idx++;
        if (idx >= text.length) {
            clearInterval(interval);
        }
    }, 15);
}
