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
    // Get progress data from the page
    const progressData = window.postProgressData || { currentPage: 1, totalPages: 5 };
    window.postProgress = new PostProgress(progressData.currentPage, progressData.totalPages);
}); 