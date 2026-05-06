/**
 * LMS Module - How Agents Work
 * Core functionality: Navigation, Quiz, Progress Tracking
 */

// ============================================
// STATE MANAGEMENT
// ============================================

const state = {
    currentLesson: null,
    completedLessons: [],
    quizScores: {},
    lessons: [],
    glossary: []
};

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🎓 LMS Module Loading...');

    // Load data from lessons.js
    if (typeof window.lessonsData !== 'undefined') {
        state.lessons = window.lessonsData;
        state.glossary = window.glossaryData || [];
    } else {
        console.error('Lessons data not loaded!');
        return;
    }

    // Load saved progress from localStorage
    loadProgress();

    // Initialize UI
    renderLessonList();
    renderGlossary();
    setupEventListeners();

    // Load first lesson or from URL hash
    const hash = window.location.hash.slice(1);
    const lessonToLoad = hash || state.lessons[0].id;
    navigateToLesson(lessonToLoad);

    console.log('✅ LMS Module Ready');
});

// ============================================
// PROGRESS MANAGEMENT
// ============================================

function loadProgress() {
    try {
        const saved = localStorage.getItem('lms_progress');
        if (saved) {
            const data = JSON.parse(saved);
            state.completedLessons = data.completedLessons || [];
            state.quizScores = data.quizScores || {};
        }
    } catch (error) {
        console.warn('Could not load progress:', error);
    }
}

function saveProgress() {
    try {
        localStorage.setItem('lms_progress', JSON.stringify({
            completedLessons: state.completedLessons,
            quizScores: state.quizScores
        }));
        updateProgressBar();
    } catch (error) {
        console.warn('Could not save progress:', error);
    }
}

function markLessonComplete(lessonId) {
    if (!state.completedLessons.includes(lessonId)) {
        state.completedLessons.push(lessonId);
        saveProgress();
        renderLessonList();
        checkAllComplete();
    }
}

function updateProgressBar() {
    const total = state.lessons.length;
    const completed = state.completedLessons.length;
    const percentage = (completed / total) * 100;

    const progressBar = document.getElementById('progressBar');
    if (progressBar) {
        progressBar.style.width = percentage + '%';
        progressBar.setAttribute('aria-valuenow', percentage);
    }
}

function resetProgress() {
    if (confirm('Are you sure you want to reset all progress? This cannot be undone.')) {
        state.completedLessons = [];
        state.quizScores = {};
        localStorage.removeItem('lms_progress');
        updateProgressBar();
        renderLessonList();
        alert('Progress reset successfully!');
    }
}

function checkAllComplete() {
    if (state.completedLessons.length === state.lessons.length) {
        setTimeout(() => showCompletionModal(), 500);
    }
}

// ============================================
// NAVIGATION
// ============================================

function renderLessonList() {
    const listElement = document.getElementById('lessonList');
    if (!listElement) return;

    listElement.innerHTML = state.lessons.map(lesson => {
        const isActive = state.currentLesson === lesson.id;
        const isCompleted = state.completedLessons.includes(lesson.id);

        return `
            <li class="lesson-item">
                <a href="#${lesson.id}"
                   class="lesson-link ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}"
                   data-lesson="${lesson.id}"
                   aria-current="${isActive ? 'page' : 'false'}">
                    <span class="lesson-number">${lesson.moduleNumber}</span>
                    <span class="lesson-text">${lesson.title}</span>
                </a>
            </li>
        `;
    }).join('');

    updateProgressBar();
}

function navigateToLesson(lessonId) {
    const lesson = state.lessons.find(l => l.id === lessonId);
    if (!lesson) {
        console.error('Lesson not found:', lessonId);
        return;
    }

    state.currentLesson = lessonId;
    window.location.hash = lessonId;

    renderLessonContent(lesson);
    renderLessonList();

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function renderLessonContent(lesson) {
    const container = document.getElementById('lessonContent');
    if (!container) return;

    container.innerHTML = `
        <article>
            <header>
                <h1 class="lesson-title">${lesson.title}</h1>
                <p class="lesson-subtitle">${lesson.subtitle}</p>

                <div class="lesson-meta">
                    <span class="meta-item">
                        <span>⏱️</span>
                        <span>${lesson.duration}</span>
                    </span>
                    <span class="meta-item">
                        <span>📊</span>
                        <span>${lesson.difficulty}</span>
                    </span>
                    <span class="meta-item">
                        <span>📝</span>
                        <span>Module ${lesson.moduleNumber}</span>
                    </span>
                </div>
            </header>

            <section class="lesson-objectives">
                <h2>Learning Objectives</h2>
                <ul>
                    ${lesson.objectives.map(obj => `<li>${obj}</li>`).join('')}
                </ul>
            </section>

            <section class="lesson-body">
                ${lesson.content}
            </section>

            ${lesson.diagram ? renderDiagram(lesson.diagram) : ''}

            ${lesson.quiz ? renderQuiz(lesson.quiz, lesson.id) : ''}

            <footer class="lesson-footer">
                <button class="btn btn-primary" onclick="markLessonComplete('${lesson.id}')">
                    Mark as Complete ✓
                </button>
            </footer>
        </article>
    `;

    updateNavigationButtons();
}

function renderDiagram(diagram) {
    return `
        <section class="diagram-section">
            <h3>${diagram.title}</h3>
            <p>${diagram.description}</p>
            ${diagram.content}
        </section>
    `;
}

function updateNavigationButtons() {
    const currentIndex = state.lessons.findIndex(l => l.id === state.currentLesson);

    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');

    if (prevBtn) {
        if (currentIndex > 0) {
            prevBtn.style.display = 'block';
            prevBtn.onclick = () => navigateToLesson(state.lessons[currentIndex - 1].id);
        } else {
            prevBtn.style.display = 'none';
        }
    }

    if (nextBtn) {
        if (currentIndex < state.lessons.length - 1) {
            nextBtn.style.display = 'block';
            nextBtn.onclick = () => navigateToLesson(state.lessons[currentIndex + 1].id);
        } else {
            nextBtn.style.display = 'none';
        }
    }
}

// ============================================
// QUIZ FUNCTIONALITY
// ============================================

function renderQuiz(quiz, lessonId) {
    return `
        <section class="quiz-container">
            <h2 class="quiz-title">📝 Knowledge Check</h2>
            <p>Test your understanding of the concepts covered in this lesson.</p>

            ${quiz.questions.map((q, idx) => `
                <div class="quiz-question" data-question-id="${q.id}">
                    <p class="question-text"><strong>Question ${idx + 1}:</strong> ${q.question}</p>
                    <div class="quiz-options">
                        ${q.options.map((option, optIdx) => `
                            <label class="quiz-option">
                                <input type="radio"
                                       name="question-${q.id}"
                                       value="${optIdx}"
                                       onchange="checkAnswer('${lessonId}', '${q.id}', ${optIdx}, ${q.correct})">
                                <span>${option}</span>
                            </label>
                        `).join('')}
                    </div>
                    <div id="feedback-${q.id}" class="quiz-feedback" style="display: none;"></div>
                </div>
            `).join('')}

            <div id="quiz-score-${lessonId}" class="quiz-score" style="display: none;"></div>
        </section>
    `;
}

function checkAnswer(lessonId, questionId, selected, correct) {
    const feedbackEl = document.getElementById(`feedback-${questionId}`);
    const question = state.lessons
        .find(l => l.id === lessonId)
        .quiz.questions
        .find(q => q.id === questionId);

    if (!feedbackEl || !question) return;

    const isCorrect = selected === correct;

    // Update UI
    const optionEls = document.querySelectorAll(`input[name="question-${questionId}"]`);
    optionEls.forEach((el, idx) => {
        const label = el.closest('.quiz-option');
        label.classList.remove('correct', 'incorrect', 'selected');

        if (idx === selected) {
            label.classList.add(isCorrect ? 'correct' : 'incorrect');
        }
    });

    // Show feedback
    feedbackEl.style.display = 'block';
    feedbackEl.className = `quiz-feedback ${isCorrect ? 'correct' : 'incorrect'}`;
    feedbackEl.innerHTML = `
        <strong>${isCorrect ? '✓ Correct!' : '✗ Incorrect'}</strong><br>
        ${question.explanation}
    `;

    // Track score
    if (!state.quizScores[lessonId]) {
        state.quizScores[lessonId] = {};
    }
    state.quizScores[lessonId][questionId] = isCorrect;
    saveProgress();

    // Check if all questions answered
    const lesson = state.lessons.find(l => l.id === lessonId);
    const totalQuestions = lesson.quiz.questions.length;
    const answeredQuestions = Object.keys(state.quizScores[lessonId] || {}).length;

    if (answeredQuestions === totalQuestions) {
        showQuizScore(lessonId);
    }
}

function showQuizScore(lessonId) {
    const scoreEl = document.getElementById(`quiz-score-${lessonId}`);
    if (!scoreEl) return;

    const scores = state.quizScores[lessonId] || {};
    const correct = Object.values(scores).filter(v => v).length;
    const total = Object.keys(scores).length;
    const percentage = Math.round((correct / total) * 100);

    scoreEl.style.display = 'block';
    scoreEl.innerHTML = `
        📊 Quiz Score: ${correct}/${total} (${percentage}%)
        ${percentage >= 70 ? '🎉 Great job!' : '💪 Keep learning!'}
    `;
}

// ============================================
// GLOSSARY
// ============================================

function renderGlossary() {
    const container = document.getElementById('glossaryContent');
    if (!container) return;

    container.innerHTML = state.glossary.map(term => `
        <div class="glossary-term">
            <div class="term-word">${term.term}</div>
            <div class="term-definition">${term.definition}</div>
        </div>
    `).join('');
}

function toggleGlossary() {
    const panel = document.getElementById('glossaryPanel');
    if (panel) {
        panel.classList.toggle('open');
    }
}

// ============================================
// COMPLETION MODAL
// ============================================

function showCompletionModal() {
    const modal = document.getElementById('completionModal');
    const textEl = document.getElementById('completionText');

    if (!modal || !textEl) return;

    const totalQuizzes = Object.keys(state.quizScores).length;
    const totalScore = Object.values(state.quizScores).reduce((sum, quiz) => {
        const correct = Object.values(quiz).filter(v => v).length;
        const total = Object.keys(quiz).length;
        return sum + (correct / total);
    }, 0);
    const avgScore = totalQuizzes > 0 ? Math.round((totalScore / totalQuizzes) * 100) : 0;

    textEl.innerHTML = `
        <p>You've completed all ${state.lessons.length} lessons!</p>
        <p><strong>Your Stats:</strong></p>
        <ul style="text-align: left; display: inline-block;">
            <li>Lessons Completed: ${state.completedLessons.length}/${state.lessons.length}</li>
            <li>Average Quiz Score: ${avgScore}%</li>
            <li>Total Quizzes: ${totalQuizzes}</li>
        </ul>
        <p><strong>🎯 Next Steps:</strong></p>
        <p>Continue your learning journey with Modules 03-09 in the full curriculum!</p>
    `;

    modal.style.display = 'flex';
}

function hideCompletionModal() {
    const modal = document.getElementById('completionModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// ============================================
// EVENT LISTENERS
// ============================================

function setupEventListeners() {
    // Glossary toggle
    const glossaryBtn = document.getElementById('glossaryBtn');
    if (glossaryBtn) {
        glossaryBtn.addEventListener('click', toggleGlossary);
    }

    const closeGlossary = document.getElementById('closeGlossary');
    if (closeGlossary) {
        closeGlossary.addEventListener('click', toggleGlossary);
    }

    // Reset progress
    const resetBtn = document.getElementById('resetBtn');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetProgress);
    }

    // Completion modal
    const closeModal = document.getElementById('closeModal');
    if (closeModal) {
        closeModal.addEventListener('click', hideCompletionModal);
    }

    // Hash change (browser back/forward)
    window.addEventListener('hashchange', () => {
        const lessonId = window.location.hash.slice(1);
        if (lessonId && lessonId !== state.currentLesson) {
            navigateToLesson(lessonId);
        }
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Escape to close glossary or modal
        if (e.key === 'Escape') {
            const glossary = document.getElementById('glossaryPanel');
            const modal = document.getElementById('completionModal');

            if (glossary && glossary.classList.contains('open')) {
                toggleGlossary();
            } else if (modal && modal.style.display === 'flex') {
                hideCompletionModal();
            }
        }
    });
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function getCurrentLessonIndex() {
    return state.lessons.findIndex(l => l.id === state.currentLesson);
}

// Expose functions for inline event handlers
window.markLessonComplete = markLessonComplete;
window.checkAnswer = checkAnswer;
window.navigateToLesson = navigateToLesson;

console.log('📚 LMS Script Loaded');
