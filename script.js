/**
 * INTELI PRESENTATION - Interactive Slides
 * Visões de Arquitetura de Sistemas Distribuídos
 * Módulo ES09 - Turma T13
 */

// ========================================
// GLOBAL VARIABLES
// ========================================
let currentSlide = 1;
const totalSlides = 30;
let timerIntervals = {};

// ========================================
// INITIALIZATION
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    initializePresentation();
    setupKeyboardNavigation();
    updateProgress();
});

function initializePresentation() {
    showSlide(1);
    updateSlideCounter();
    updateNavigationButtons();
}

// ========================================
// SLIDE NAVIGATION
// ========================================
function changeSlide(direction) {
    const newSlide = currentSlide + direction;
    if (newSlide >= 1 && newSlide <= totalSlides) {
        showSlide(newSlide);
    }
}

function showSlide(slideNumber) {
    // Hide all slides
    const slides = document.querySelectorAll('.slide');
    slides.forEach(slide => {
        slide.classList.remove('active');
    });
    
    // Show target slide
    const targetSlide = document.querySelector(`[data-slide="${slideNumber}"]`);
    if (targetSlide) {
        targetSlide.classList.add('active');
        currentSlide = slideNumber;
        updateSlideCounter();
        updateNavigationButtons();
        updateProgress();
    }
}

function goToSlide(slideNumber) {
    if (slideNumber >= 1 && slideNumber <= totalSlides) {
        showSlide(slideNumber);
    }
}

function updateSlideCounter() {
    const counter = document.getElementById('slideCounter');
    if (counter) {
        counter.textContent = `${currentSlide} / ${totalSlides}`;
    }
}

function updateNavigationButtons() {
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    if (prevBtn) {
        prevBtn.disabled = currentSlide === 1;
    }
    if (nextBtn) {
        nextBtn.disabled = currentSlide === totalSlides;
    }
}

function updateProgress() {
    const progressBar = document.getElementById('progressBar');
    if (progressBar) {
        const progress = (currentSlide / totalSlides) * 100;
        progressBar.style.width = `${progress}%`;
    }
}

// ========================================
// KEYBOARD NAVIGATION
// ========================================
function setupKeyboardNavigation() {
    document.addEventListener('keydown', function(event) {
        switch(event.key) {
            case 'ArrowRight':
            case 'ArrowDown':
            case ' ':
            case 'PageDown':
                event.preventDefault();
                changeSlide(1);
                break;
            case 'ArrowLeft':
            case 'ArrowUp':
            case 'PageUp':
                event.preventDefault();
                changeSlide(-1);
                break;
            case 'Home':
                event.preventDefault();
                goToSlide(1);
                break;
            case 'End':
                event.preventDefault();
                goToSlide(totalSlides);
                break;
            case 'Escape':
                closeModal();
                break;
            case 'f':
            case 'F':
                toggleFullscreen();
                break;
        }
    });
}

// ========================================
// FULLSCREEN
// ========================================
function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(err => {
            console.log(`Error attempting to enable fullscreen: ${err.message}`);
        });
    } else {
        document.exitFullscreen();
    }
}

// ========================================
// QUIZ FUNCTIONALITY
// ========================================
function checkAnswer(button, questionNumber) {
    const options = button.parentElement.querySelectorAll('.quiz-option');
    const isCorrect = button.dataset.correct === 'true';
    const feedbackElement = document.getElementById(`feedback-q${questionNumber}`);
    
    // Disable all options
    options.forEach(option => {
        option.classList.add('disabled');
        if (option.dataset.correct === 'true') {
            option.classList.add('correct');
        } else if (option === button && !isCorrect) {
            option.classList.add('incorrect');
        }
    });
    
    // Show feedback
    if (feedbackElement) {
        feedbackElement.classList.add('show');
        if (isCorrect) {
            feedbackElement.classList.add('correct');
            feedbackElement.textContent = '✓ Correto! Excelente!';
        } else {
            feedbackElement.classList.add('incorrect');
            feedbackElement.textContent = '✗ Incorreto. Veja a resposta correta destacada.';
        }
    }
}

// ========================================
// TIMER FUNCTIONALITY
// ========================================
function startTimer(timerId, seconds) {
    const timerElement = document.getElementById(timerId);
    if (!timerElement) return;
    
    const timerValue = timerElement.querySelector('.timer-value');
    const timerBtn = timerElement.nextElementSibling;
    
    // Clear existing interval if any
    if (timerIntervals[timerId]) {
        clearInterval(timerIntervals[timerId]);
    }
    
    let remainingSeconds = seconds;
    
    // Update button
    timerBtn.textContent = 'Pausar';
    timerBtn.onclick = () => pauseTimer(timerId, remainingSeconds);
    
    // Start countdown
    timerIntervals[timerId] = setInterval(() => {
        remainingSeconds--;
        
        if (remainingSeconds <= 0) {
            clearInterval(timerIntervals[timerId]);
            timerValue.textContent = '00:00';
            timerBtn.textContent = 'Reiniciar';
            timerBtn.onclick = () => startTimer(timerId, seconds);
            
            // Play sound or visual alert
            timerElement.style.animation = 'pulse 0.5s ease-in-out 3';
            setTimeout(() => {
                timerElement.style.animation = '';
            }, 1500);
        } else {
            timerValue.textContent = formatTime(remainingSeconds);
        }
    }, 1000);
    
    // Initial display
    timerValue.textContent = formatTime(remainingSeconds);
}

function pauseTimer(timerId, currentSeconds) {
    const timerElement = document.getElementById(timerId);
    if (!timerElement) return;
    
    const timerBtn = timerElement.nextElementSibling;
    
    if (timerIntervals[timerId]) {
        clearInterval(timerIntervals[timerId]);
        timerIntervals[timerId] = null;
        timerBtn.textContent = 'Continuar';
        timerBtn.onclick = () => startTimer(timerId, currentSeconds);
    }
}

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// ========================================
// VIEWPOINT MODAL
// ========================================
const viewpointDetails = {
    enterprise: {
        title: 'Enterprise Viewpoint',
        color: '#4a90d9',
        content: `
            <h3 style="color: #4a90d9;">Visão de Negócio</h3>
            <p><strong>Foco:</strong> Propósito, escopo e políticas do sistema.</p>
            <p>Esta visão descreve os requisitos de negócio e como o sistema deve atendê-los. É a visão mais abstrata, focando no "porquê" do sistema existir.</p>
            <h4>Elementos principais:</h4>
            <ul>
                <li>Objetivos de negócio</li>
                <li>Stakeholders e seus papéis</li>
                <li>Políticas e regras de negócio</li>
                <li>Comunidades e contratos</li>
            </ul>
            <h4>Aplicação no projeto ASIS:</h4>
            <p>Define os objetivos de compliance tributário, os stakeholders (clientes, fisco, equipe interna) e as políticas de qualidade de serviço.</p>
        `
    },
    information: {
        title: 'Information Viewpoint',
        color: '#50c878',
        content: `
            <h3 style="color: #50c878;">Visão de Informação</h3>
            <p><strong>Foco:</strong> Semântica da informação e processamento de dados.</p>
            <p>Esta visão descreve a informação gerenciada pelo sistema, sua estrutura e tipos de conteúdo. Foca no "o quê" o sistema manipula.</p>
            <h4>Elementos principais:</h4>
            <ul>
                <li>Esquemas de informação</li>
                <li>Tipos de dados e estruturas</li>
                <li>Invariantes e regras de integridade</li>
                <li>Fluxos de informação</li>
            </ul>
            <h4>Aplicação no projeto ASIS:</h4>
            <p>Define os schemas de notas fiscais, estruturas de dados tributários conforme SPED, e regras de validação de CNPJ e valores.</p>
        `
    },
    computational: {
        title: 'Computational Viewpoint',
        color: '#9b59b6',
        content: `
            <h3 style="color: #9b59b6;">Visão Computacional</h3>
            <p><strong>Foco:</strong> Decomposição funcional do sistema.</p>
            <p>Esta visão habilita a distribuição através da decomposição do sistema em objetos que interagem via interfaces. Foca no "como" funciona.</p>
            <h4>Elementos principais:</h4>
            <ul>
                <li>Objetos computacionais</li>
                <li>Interfaces e operações</li>
                <li>Bindings e interações</li>
                <li>Contratos de interface</li>
            </ul>
            <h4>Aplicação no projeto ASIS:</h4>
            <p>Define os serviços (Cálculo, Validação, Gateway), suas APIs REST documentadas em OpenAPI, e as operações disponíveis.</p>
        `
    },
    engineering: {
        title: 'Engineering Viewpoint',
        color: '#e67e22',
        content: `
            <h3 style="color: #e67e22;">Visão de Engenharia</h3>
            <p><strong>Foco:</strong> Mecanismos de distribuição e infraestrutura.</p>
            <p>Esta visão descreve como os objetos computacionais são distribuídos e como se comunicam. Foca no "onde" e "como" é executado.</p>
            <h4>Elementos principais:</h4>
            <ul>
                <li>Nós e clusters</li>
                <li>Canais de comunicação</li>
                <li>Transparências de distribuição</li>
                <li>Mecanismos de failover</li>
            </ul>
            <h4>Aplicação no projeto ASIS:</h4>
            <p>Define a arquitetura de microserviços em Kubernetes, comunicação REST/Filas, e estratégias de auto-scaling horizontal.</p>
        `
    },
    technology: {
        title: 'Technology Viewpoint',
        color: '#1abc9c',
        content: `
            <h3 style="color: #1abc9c;">Visão Tecnológica</h3>
            <p><strong>Foco:</strong> Escolha de tecnologias específicas.</p>
            <p>Esta visão descreve as tecnologias concretas escolhidas para implementar o sistema. É a visão mais concreta.</p>
            <h4>Elementos principais:</h4>
            <ul>
                <li>Linguagens e frameworks</li>
                <li>Bancos de dados e storage</li>
                <li>Infraestrutura de cloud</li>
                <li>Ferramentas de DevOps</li>
            </ul>
            <h4>Aplicação no projeto ASIS:</h4>
            <p>Define o uso de Java/Spring Boot, PostgreSQL/Redis, AWS/Azure, Docker/Kubernetes, e ferramentas de CI/CD.</p>
        `
    }
};

function showViewpointDetail(viewpoint) {
    const modal = document.getElementById('viewpointModal');
    const modalBody = document.getElementById('modalBody');
    
    if (modal && modalBody && viewpointDetails[viewpoint]) {
        modalBody.innerHTML = viewpointDetails[viewpoint].content;
        modal.classList.add('active');
    }
}

function closeModal() {
    const modal = document.getElementById('viewpointModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

// Close modal on outside click
document.addEventListener('click', function(event) {
    const modal = document.getElementById('viewpointModal');
    if (event.target === modal) {
        closeModal();
    }
});

// ========================================
// TOUCH SUPPORT
// ========================================
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', function(event) {
    touchStartX = event.changedTouches[0].screenX;
}, false);

document.addEventListener('touchend', function(event) {
    touchEndX = event.changedTouches[0].screenX;
    handleSwipe();
}, false);

function handleSwipe() {
    const swipeThreshold = 50;
    const diff = touchStartX - touchEndX;
    
    if (Math.abs(diff) > swipeThreshold) {
        if (diff > 0) {
            // Swipe left - next slide
            changeSlide(1);
        } else {
            // Swipe right - previous slide
            changeSlide(-1);
        }
    }
}

// ========================================
// PRESENTER NOTES (for future use)
// ========================================
const presenterNotes = {
    1: "Slide de abertura. Apresentar-se e contextualizar o módulo ES09.",
    2: "Revisar os três objetivos principais da aula. Conectar com o autoestudo.",
    3: "Apresentar a agenda. Destacar os momentos de atividade prática.",
    4: "Quiz de aquecimento - dar tempo para os alunos responderem.",
    5: "Segunda pergunta do quiz sobre Enterprise Viewpoint.",
    6: "Terceira pergunta sobre Business Drivers.",
    7: "Contextualizar o desafio da ASIS. Fazer a pergunta retórica.",
    8: "Diagrama interativo - incentivar cliques para explorar cada visão.",
    // ... adicionar mais notas conforme necessário
};

function getPresenterNote(slideNumber) {
    return presenterNotes[slideNumber] || "Sem notas para este slide.";
}

// ========================================
// ANIMATION HELPERS
// ========================================
function addPulseAnimation(element) {
    element.style.animation = 'pulse 0.5s ease-in-out';
    setTimeout(() => {
        element.style.animation = '';
    }, 500);
}

// CSS Animation keyframes (added via JS for pulse effect)
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
`;
document.head.appendChild(style);

// ========================================
// EXPORT/PRINT FUNCTIONALITY
// ========================================
function printPresentation() {
    window.print();
}

// ========================================
// ACCESSIBILITY
// ========================================
function announceSlide(slideNumber) {
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', 'polite');
    announcement.className = 'sr-only';
    announcement.textContent = `Slide ${slideNumber} de ${totalSlides}`;
    document.body.appendChild(announcement);
    setTimeout(() => announcement.remove(), 1000);
}

// ========================================
// DEBUG MODE (for development)
// ========================================
const DEBUG = false;

function debugLog(message) {
    if (DEBUG) {
        console.log(`[Presentation Debug] ${message}`);
    }
}

// Log initialization
debugLog('Presentation initialized successfully');
