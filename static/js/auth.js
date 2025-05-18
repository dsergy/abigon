// Helper for safe fetch requests with CSRF
const csrfFetch = (url, options = {}) => {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    return fetch(url, {
        ...options,
        credentials: 'same-origin',
        headers: {
            ...options.headers,
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    });
};

// Helper for safe Bootstrap modal instance
const getOrCreateModal = (element) => {
    if (!element) return null;
    return bootstrap.Modal.getOrCreateInstance(element);
};

// Helper for focus and inert management
const setModalInert = (modal, inert = true) => {
    if (!modal) return;
    const content = modal.querySelector('.modal-content');
    if (content) {
        content.inert = inert;
    }
};

// Helper for loading forms into modals
const loadForm = async (url, modalElement) => {
    try {
        const response = await csrfFetch(url);
        if (!response.ok) throw new Error('Network response was not ok');
        const html = await response.text();
        modalElement.querySelector('.modal-content').innerHTML = html;
        return true;
    } catch (error) {
        console.error('Error loading form:', error);
        alert('Failed to load form. Please try again.');
        return false;
    }
};

// Helper for handling JSON responses
const handleResponse = async (response) => {
    const data = await response.json();
    if (data.status === 'error') {
        throw new Error(data.message);
    }
    return data;
};

document.addEventListener('DOMContentLoaded', function () {
    // Get modal elements
    const loginModal = document.getElementById('loginModal');
    const registerModal = document.getElementById('registerModal');
    const passwordResetModal = document.getElementById('passwordResetModal');

    // Handle modal switching
    document.addEventListener('click', async function (e) {
        if (e.target.matches('.register-link')) {
            e.preventDefault();
            const loginModalInstance = getOrCreateModal(loginModal);
            const registerModalInstance = getOrCreateModal(registerModal);
            loginModalInstance.hide();
            registerModalInstance.show();
        }
        if (e.target.matches('.login-link')) {
            e.preventDefault();
            const registerModalInstance = getOrCreateModal(registerModal);
            const loginModalInstance = getOrCreateModal(loginModal);
            registerModalInstance.hide();
            loginModalInstance.show();
        }
        if (e.target.matches('#forgotPassword')) {
            e.preventDefault();
            const loginModalInstance = getOrCreateModal(loginModal);
            const passwordResetModalInstance = getOrCreateModal(passwordResetModal);
            loginModalInstance.hide();
            passwordResetModalInstance.show();
        }
    });

    // Handle form submissions
    document.addEventListener('submit', async function (e) {
        const form = e.target;
        if (form.classList.contains('login-form') ||
            form.classList.contains('register-form') ||
            form.classList.contains('verify-form') ||
            form.classList.contains('set-password-form')) {
            e.preventDefault();

            const submitButton = form.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
            submitButton.disabled = true;
            submitButton.innerHTML = 'Processing...';

            try {
                const formData = new FormData(form);
                const response = await csrfFetch(form.action, {
                    method: 'POST',
                    body: formData
                });

                const data = await handleResponse(response);

                if (data.redirect) {
                    window.location.href = data.redirect;
                    return;
                }

                if (data.html) {
                    const modalContent = form.closest('.modal-content');
                    if (modalContent) {
                        modalContent.innerHTML = data.html;
                    }
                }
            } catch (error) {
                console.error('Error:', error);
                const errorDiv = document.createElement('div');
                errorDiv.className = 'alert alert-danger';
                errorDiv.textContent = error.message || 'An error occurred. Please try again.';
                form.insertBefore(errorDiv, form.firstChild);
            } finally {
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
            }
        }
    });

    // Handle password reset code sending
    document.addEventListener('click', async function (e) {
        if (e.target.matches('#sendResetCode')) {
            e.preventDefault();
            const form = document.getElementById('resetPasswordForm');
            if (!form) return;

            try {
                const formData = new FormData(form);
                const response = await csrfFetch('/accounts/password-reset/', {
                    method: 'POST',
                    body: formData
                });

                const data = await handleResponse(response);
                if (data.html) {
                    const modalContent = form.closest('.modal-content');
                    if (modalContent) {
                        modalContent.innerHTML = data.html;
                    }
                }
            } catch (error) {
                console.error('Error:', error);
                const errorDiv = document.createElement('div');
                errorDiv.className = 'alert alert-danger';
                errorDiv.textContent = error.message || 'An error occurred. Please try again.';
                form.insertBefore(errorDiv, form.firstChild);
            }
        }
    });

    // Focus and inert management for modals
    [loginModal, registerModal, passwordResetModal].forEach(modal => {
        if (!modal) return;

        modal.addEventListener('show.bs.modal', () => {
            setModalInert(modal, false);
        });

        modal.addEventListener('hide.bs.modal', () => {
            setModalInert(modal, true);
            // Remove focus from active element
            if (document.activeElement instanceof HTMLElement) {
                document.activeElement.blur();
            }
        });

        modal.addEventListener('hidden.bs.modal', () => {
            // Clear modal content after hiding
            const content = modal.querySelector('.modal-content');
            if (content) {
                content.innerHTML = '';
            }
        });
    });
}); 