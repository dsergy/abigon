class PostProgress {
    constructor(currentPage, totalPages) {
        this.currentPage = currentPage;
        this.totalPages = totalPages;
        this.init();
    }

    init() {
        this.createProgressDots();
        this.updateProgress();
        this.attachEventListeners();
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
            dot.dataset.step = i;

            const number = document.createElement('span');
            number.className = 'dot-number';
            number.textContent = i;

            const label = document.createElement('span');
            label.className = 'dot-label';
            label.textContent = this.getStepLabel(i);

            dot.appendChild(number);
            dot.appendChild(label);
            dotsContainer.appendChild(dot);

            if (i < this.totalPages) {
                const line = document.createElement('div');
                line.className = 'progress-line';
                dotsContainer.appendChild(line);
            }
        }

        progressContainer.appendChild(dotsContainer);
    }

    getStepLabel(step) {
        const labels = {
            1: 'Basic Info',
            2: 'Details',
            3: 'Photos',
            4: 'Contact',
            5: 'Preview'
        };
        return labels[step] || `Step ${step}`;
    }

    updateProgress() {
        const dots = document.querySelectorAll('.progress-dot');
        const lines = document.querySelectorAll('.progress-line');

        dots.forEach((dot, index) => {
            const pageNumber = index + 1;
            dot.classList.remove('active', 'completed');

            if (pageNumber < this.currentPage) {
                dot.classList.add('completed');
            } else if (pageNumber === this.currentPage) {
                dot.classList.add('active');
            }
        });

        // Update lines
        lines.forEach((line, index) => {
            if (index + 1 < this.currentPage) {
                line.classList.add('completed');
            } else {
                line.classList.remove('completed');
            }
        });
    }

    attachEventListeners() {
        const dots = document.querySelectorAll('.progress-dot');
        dots.forEach(dot => {
            dot.addEventListener('click', (e) => {
                const step = parseInt(dot.dataset.step);
                if (step <= this.currentPage + 1) {
                    this.handleStepClick(step);
                }
            });

            // Add hover effect
            dot.addEventListener('mouseenter', () => {
                if (parseInt(dot.dataset.step) <= this.currentPage + 1) {
                    dot.style.transform = 'scale(1.1)';
                }
            });

            dot.addEventListener('mouseleave', () => {
                dot.style.transform = 'scale(1)';
            });
        });
    }

    handleStepClick(step) {
        if (step <= this.currentPage + 1) {
            this.currentPage = step;
            this.updateProgress();

            // Emit custom event for step change
            const event = new CustomEvent('stepChanged', {
                detail: {
                    step: step,
                    label: this.getStepLabel(step)
                }
            });
            document.dispatchEvent(event);

            // Add animation class
            const dot = document.querySelector(`.progress-dot[data-step="${step}"]`);
            if (dot) {
                dot.classList.add('animate');
                setTimeout(() => dot.classList.remove('animate'), 500);
            }
        }
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

    // Create progress instance
    const progress = new PostProgress(currentStep, 5);

    // Handle step changes
    document.addEventListener('stepChanged', function (e) {
        const { step, label } = e.detail;
        console.log(`Step changed to ${step}: ${label}`);

        // Update URL without page reload
        const url = new URL(window.location.href);
        url.searchParams.set('step', step);
        window.history.pushState({}, '', url);

        // Load content for the new step
        loadStepContent(step);
    });
});

// Function to load step content
async function loadStepContent(step) {
    try {
        const response = await fetch(`/ads/post/step/${step}/`);
        if (!response.ok) throw new Error('Failed to load step content');

        const content = await response.text();
        const contentContainer = document.querySelector('#post-content');
        if (contentContainer) {
            // Add fade out effect
            contentContainer.style.opacity = '0';

            setTimeout(() => {
                contentContainer.innerHTML = content;
                // Add fade in effect
                contentContainer.style.opacity = '1';
            }, 300);
        }
    } catch (error) {
        console.error('Error loading step content:', error);
        // Show error message
        const errorContainer = document.querySelector('#post-content');
        if (errorContainer) {
            errorContainer.innerHTML = `
                <div class="alert alert-danger">
                    Failed to load content. Please try again.
                </div>
            `;
        }
    }
} 