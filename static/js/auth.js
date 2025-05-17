document.addEventListener('DOMContentLoaded', function () {
    // Get modal elements
    const loginModal = document.getElementById('loginModal');
    const registerModal = document.getElementById('registerModal');

    // Get CSRF token from cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Load login form when login modal is shown
    loginModal.addEventListener('show.bs.modal', function (event) {
        fetch('/accounts/login/', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => response.text())
            .then(html => {
                this.querySelector('.modal-content').innerHTML = html;
            });
    });

    // Load register form when register modal is shown
    registerModal.addEventListener('show.bs.modal', function (event) {
        fetch('/accounts/register/', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => response.text())
            .then(html => {
                this.querySelector('.modal-content').innerHTML = html;
            });
    });

    // Handle modal switching
    document.addEventListener('click', function (e) {
        if (e.target.matches('.register-link')) {
            e.preventDefault();
            const loginModal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
            const registerModal = new bootstrap.Modal(document.getElementById('registerModal'));
            loginModal.hide();
            registerModal.show();
        }
        if (e.target.matches('.login-link')) {
            e.preventDefault();
            const registerModal = bootstrap.Modal.getInstance(document.getElementById('registerModal'));
            const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
            registerModal.hide();
            loginModal.show();
        }
    });

    // Handle form submissions
    document.addEventListener('submit', function (e) {
        const form = e.target;
        if (form.classList.contains('login-form') ||
            form.classList.contains('register-form') ||
            form.classList.contains('verify-form') ||
            form.classList.contains('set-password-form')) {
            e.preventDefault();

            // Remove any existing error messages
            const existingError = form.querySelector('.alert');
            if (existingError) {
                existingError.remove();
            }

            const formData = new FormData(form);

            // Get the CSRF token
            const csrfToken = getCookie('csrftoken');

            // Disable form submission while processing
            const submitButton = form.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
            submitButton.disabled = true;
            submitButton.innerHTML = 'Processing...';

            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then(response => {
                    if (!response.ok && response.status !== 400) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.text();
                })
                .then(responseText => {
                    // Re-enable submit button
                    submitButton.disabled = false;
                    submitButton.innerHTML = originalButtonText;

                    try {
                        // Try to parse as JSON first
                        const jsonResponse = JSON.parse(responseText);
                        if (jsonResponse.error) {
                            throw new Error(jsonResponse.error);
                        }
                        if (jsonResponse.redirect) {
                            window.location.href = jsonResponse.redirect;
                            return;
                        }
                    } catch (e) {
                        // Not JSON, handle as HTML
                        if (responseText.includes('window.location.href')) {
                            // Successful login with redirect
                            eval(responseText);
                        } else if (responseText.includes('modal-content')) {
                            // Server returned a new form with errors or next step
                            const modalContent = form.closest('.modal-content');
                            if (modalContent) {
                                modalContent.innerHTML = responseText;
                            } else {
                                // If somehow we lost modal context, show in register modal
                                registerModal.querySelector('.modal-content').innerHTML = responseText;
                            }
                        } else {
                            // Show generic error message
                            const errorDiv = document.createElement('div');
                            errorDiv.className = 'alert alert-danger';
                            errorDiv.textContent = 'An error occurred. Please try again.';
                            form.insertBefore(errorDiv, form.firstChild);
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    submitButton.disabled = false;
                    submitButton.innerHTML = originalButtonText;

                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'alert alert-danger';
                    errorDiv.textContent = error.message || 'An error occurred. Please try again.';
                    form.insertBefore(errorDiv, form.firstChild);
                });
        }
    });

    // Clean up modal content when hidden
    [loginModal, registerModal].forEach(modal => {
        modal.addEventListener('hidden.bs.modal', function () {
            this.querySelector('.modal-content').innerHTML = '';
        });
    });
}); 