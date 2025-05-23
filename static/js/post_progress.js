class PostProgress {
    constructor(currentPage, totalPages) {
        this.currentPage = currentPage;
        this.totalPages = totalPages;
        this.init();
    }

    init() {
        this.createProgressDots();
        this.updateProgress();
    }

    createProgressDots() {
        const progressContainer = document.querySelector('.progress-container');
        if (!progressContainer) return;

        // Clear existing content
        progressContainer.innerHTML = '';

        // Create dots container
        const dotsContainer = document.createElement('div');
        dotsContainer.className = 'progress-dots';

        // Create dots
        for (let i = 1; i <= this.totalPages; i++) {
            const dot = document.createElement('div');
            dot.className = `progress-dot ${i <= this.currentPage ? 'completed' : ''} ${i === this.currentPage ? 'active' : ''}`;

            const number = document.createElement('span');
            number.className = 'dot-number';
            number.textContent = i;

            dot.appendChild(number);
            dotsContainer.appendChild(dot);
        }

        progressContainer.appendChild(dotsContainer);
    }

    updateProgress() {
        const dots = document.querySelectorAll('.progress-dot');
        dots.forEach((dot, index) => {
            const pageNumber = index + 1;
            dot.classList.remove('active', 'completed');

            if (pageNumber < this.currentPage) {
                dot.classList.add('completed');
            } else if (pageNumber === this.currentPage) {
                dot.classList.add('active');
            }
        });
    }

    setPage(page) {
        if (page > 0 && page <= this.totalPages) {
            this.currentPage = page;
            this.updateProgress();
        }
    }
}

// Initialize progress when the page loads
document.addEventListener('DOMContentLoaded', function () {
    const progressDots = document.querySelectorAll('.progress-dot');
    let currentStep = 1;

    // Find the initial active step
    progressDots.forEach(dot => {
        if (dot.classList.contains('active')) {
            currentStep = parseInt(dot.dataset.step);
        }
    });

    function updateProgress(step) {
        progressDots.forEach(dot => {
            const dotStep = parseInt(dot.dataset.step);
            dot.classList.remove('active', 'completed');
            if (dotStep < step) {
                dot.classList.add('completed');
            } else if (dotStep === step) {
                dot.classList.add('active');
            }
        });
    }

    function handleStepClick(step) {
        if (step <= currentStep + 1) {
            currentStep = step;
            updateProgress(step);
            // Emit custom event for step change
            const event = new CustomEvent('stepChanged', {
                detail: { step: step }
            });
            document.dispatchEvent(event);
        }
    }

    progressDots.forEach(dot => {
        const step = parseInt(dot.dataset.step);
        dot.addEventListener('click', function () {
            handleStepClick(step);
        });
    });
}); 