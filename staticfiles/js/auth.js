// Global function for toggling password visibility
window.togglePassword = function (button) {
    const targetId = button.getAttribute('data-target');
    const input = document.getElementById(targetId);
    const icon = button.querySelector('i');

    if (input && icon) {
        if (input.type === 'password') {
            input.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        } else {
            input.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    }
};

// Helper for safe fetch requests with CSRF token
const csrfFetch = (url, options = {}) => {
    // Get CSRF token from either meta tag or input field
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') ||
        document.querySelector('[name=csrfmiddlewaretoken]')?.value;

    if (!csrfToken) {
        console.error("CSRF token not found");
        throw new Error("CSRF token not found");
    }

    const defaultOptions = {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json'
        },
        credentials: 'same-origin'
    };

    return fetch(url, { ...defaultOptions, ...options });
};

// Helper for safe Bootstrap modal instance management
const getOrCreateModal = (element) => {
    if (!element) {
        console.error('Modal element not found');
        return null;
    }
    return bootstrap.Modal.getOrCreateInstance(element);
};

// Helper for managing modal focus and inert states
const setModalInert = (modal, inert = true) => {
    if (!modal) return;
    const content = modal.querySelector('.modal-content');
    if (content) {
        content.inert = inert;
    }
};

// Helper for loading forms into modal windows
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

// Helper for displaying error messages in forms
function displayError(form, message) {
    if (!form) {
        console.error('Form not found');
        return;
    }

    // Create error message element
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger';
    errorDiv.textContent = message;

    // Find error container in modal content
    const modalContent = form.closest('.modal-content');
    let errorContainer = modalContent.querySelector('#registerErrorContainer');

    if (!errorContainer) {
        errorContainer = document.createElement('div');
        errorContainer.id = 'registerErrorContainer';
        const modalBody = modalContent.querySelector('.modal-body');
        if (modalBody) {
            modalBody.insertBefore(errorContainer, form);
        } else {
            modalContent.insertBefore(errorContainer, form);
        }
    }

    // Clear existing errors and add new one
    errorContainer.innerHTML = '';
    errorContainer.appendChild(errorDiv);

    // Scroll to error message
    errorContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Main initialization when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    // Get modal elements
    const loginModal = document.getElementById('loginModal');
    const registerModal = document.getElementById('registerModal');
    const emailModal = document.getElementById('emailModal');
    const verifyModal = document.getElementById('verifyModal');
    const setPasswordModal = document.getElementById('setPasswordModal');

    // Initialize modals
    let loginModalInstance;
    let registerModalInstance;
    let emailModalInstance;

    if (loginModal) {
        try {
            // Check if modal is already initialized
            loginModalInstance = bootstrap.Modal.getInstance(loginModal);
            if (!loginModalInstance) {
                loginModalInstance = new bootstrap.Modal(loginModal, {
                    backdrop: 'static',
                    keyboard: false
                });
            }
        } catch (error) {
            console.error('Error creating login modal instance:', error);
        }
    }

    if (registerModal) {
        try {
            // Check if modal is already initialized
            registerModalInstance = bootstrap.Modal.getInstance(registerModal);
            if (!registerModalInstance) {
                registerModalInstance = new bootstrap.Modal(registerModal, {
                    backdrop: 'static',
                    keyboard: false
                });
            }
        } catch (error) {
            console.error('Error creating register modal instance:', error);
        }
    }

    if (emailModal) {
        try {
            // Check if modal is already initialized
            emailModalInstance = bootstrap.Modal.getInstance(emailModal);
            if (!emailModalInstance) {
                emailModalInstance = new bootstrap.Modal(emailModal, {
                    backdrop: 'static',
                    keyboard: false
                });
            }
        } catch (error) {
            console.error('Error creating email modal instance:', error);
        }
    }

    // Function to handle login click
    function handleLoginClick(e) {
        e.preventDefault();
        e.stopPropagation();

        // Try to get existing instance or create new one
        if (!loginModalInstance) {
            try {
                loginModalInstance = bootstrap.Modal.getInstance(loginModal) || new bootstrap.Modal(loginModal, {
                    backdrop: 'static',
                    keyboard: false
                });
            } catch (error) {
                console.error('Error getting/creating login modal instance:', error);
                return;
            }
        }

        // Load form content first
        csrfFetch('/accounts/login/modal/')
            .then(response => {
                if (!response.ok) throw new Error('Failed to load login form');
                return response.text();
            })
            .then(html => {
                const modalContent = loginModal.querySelector('.modal-content');
                if (modalContent) {
                    modalContent.innerHTML = html;
                    // Show modal after content is loaded
                    loginModalInstance.show();
                } else {
                    console.error('Modal content element not found');
                }
            })
            .catch(error => {
                console.error('Error loading login form:', error);
            });
    }

    // Add click handler to document with event delegation
    document.addEventListener('click', function (e) {
        // Check if clicked element or its parent has login-link class
        const loginLink = e.target.closest('.login-link');
        if (loginLink) {
            handleLoginClick(e);
        }
    });

    // Also try direct event listener on the button
    const loginButton = document.getElementById('loginButton');
    if (loginButton) {
        loginButton.addEventListener('click', handleLoginClick);
    }

    // Load registration form when modal is shown
    registerModal.addEventListener('show.bs.modal', async function () {
        try {
            const response = await csrfFetch('/accounts/register/');
            if (!response.ok) throw new Error('Failed to load registration form');
            const html = await response.text();
            registerModal.querySelector('.modal-content').innerHTML = html;
        } catch (error) {
            console.error('Error loading registration form:', error);
        }
    });

    // Handle modal switching
    document.addEventListener('click', async function (e) {
        if (e.target.matches('.register-link')) {
            e.preventDefault();
            const loginModalInstance = getOrCreateModal(loginModal);
            const registerModalInstance = getOrCreateModal(registerModal);

            // Remove focus from active element
            if (document.activeElement instanceof HTMLElement) {
                document.activeElement.blur();
            }

            // Hide login modal first
            loginModalInstance.hide();

            // Wait for login modal to be hidden
            loginModal.addEventListener('hidden.bs.modal', function handler() {
                // Remove the event listener
                loginModal.removeEventListener('hidden.bs.modal', handler);

                // Show register modal
                registerModalInstance.show();

                // Focus first input in register form
                const firstInput = registerModal.querySelector('input');
                if (firstInput) {
                    firstInput.focus();
                }
            }, { once: true });
        }
        if (e.target.matches('.login-link')) {
            e.preventDefault();
            const registerModalInstance = getOrCreateModal(registerModal);
            const loginModalInstance = getOrCreateModal(loginModal);

            // Remove focus from active element
            if (document.activeElement instanceof HTMLElement) {
                document.activeElement.blur();
            }

            // Hide register modal first
            registerModalInstance.hide();

            // Wait for register modal to be hidden
            registerModal.addEventListener('hidden.bs.modal', function handler() {
                // Remove the event listener
                registerModal.removeEventListener('hidden.bs.modal', handler);

                // Show login modal
                loginModalInstance.show();

                // Focus first input in login form
                const firstInput = loginModal.querySelector('input');
                if (firstInput) {
                    firstInput.focus();
                }
            }, { once: true });
        }
    });

    // Handle form submissions
    document.addEventListener('submit', async function (e) {
        const form = e.target;
        if (form.classList.contains('register-form') || form.classList.contains('login-form') ||
            form.classList.contains('set-password-form') || form.classList.contains('verify-form')) {
            e.preventDefault();
            console.log('=== FORM SUBMISSION START ===');
            console.log('Form:', form);
            console.log('Form action:', form.action);

            // Get submit button and store original text
            const submitButton = form.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;

            try {
                // Disable submit button and show loading state
                submitButton.disabled = true;
                submitButton.innerHTML = 'Processing...';

                // Collect and send form data
                const formData = new FormData(form);
                console.log('Form data:', Object.fromEntries(formData.entries()));

                console.log('Sending request to:', form.action);
                const response = await csrfFetch(form.action, {
                    method: 'POST',
                    body: formData
                });
                console.log('Response status:', response.status);
                console.log('Response ok:', response.ok);

                // Get the response text first
                const text = await response.text();
                console.log('Raw server response:', text);

                // Try to parse as JSON
                let data;
                try {
                    data = JSON.parse(text);
                    console.log('Parsed JSON data:', data);

                    // Handle error response
                    if (!response.ok || data.status === 'error') {
                        const errorMessage = data.message || 'Operation failed. Please try again.';
                        console.error('Server error detected:', errorMessage);
                        console.log('Response not ok:', !response.ok);
                        console.log('Data status error:', data.status === 'error');

                        if (data.html) {
                            // Update modal content with error HTML
                            const modalContent = form.closest('.modal-content');
                            if (modalContent) {
                                modalContent.innerHTML = data.html;
                            }
                        } else {
                            displayError(form, errorMessage);
                        }
                        return;
                    }

                    // Handle successful response
                    if (data.redirect) {
                        console.log('Redirecting to:', data.redirect);
                        window.location.href = data.redirect;
                        return;
                    }

                    if (data.html) {
                        console.log('Updating modal content with HTML response');
                        const modalContent = form.closest('.modal-content');
                        if (modalContent) {
                            modalContent.innerHTML = data.html;
                            // If this is a verification form and we got a success response,
                            // we're transitioning to the password form
                            if (form.classList.contains('verify-form') && data.status === 'success') {
                                // Focus the first password input
                                const firstPasswordInput = modalContent.querySelector('input[type="password"]');
                                if (firstPasswordInput) {
                                    firstPasswordInput.focus();
                                }
                            }
                        }
                    }

                    // Handle successful registration completion
                    if (form.classList.contains('set-password-form') && data.status === 'success') {
                        // Find all modals that might be open
                        const modals = ['registerModal', 'verifyModal', 'setPasswordModal'];
                        modals.forEach(modalId => {
                            const modalElement = document.getElementById(modalId);
                            if (modalElement) {
                                const modalInstance = bootstrap.Modal.getInstance(modalElement);
                                if (modalInstance) {
                                    modalInstance.hide();
                                }
                            }
                        });

                        // Show success message
                        const successAlert = document.createElement('div');
                        successAlert.className = 'alert alert-success';
                        successAlert.innerHTML = 'Registration completed successfully! You can now login with your new account.';
                        document.querySelector('.main-content .container').prepend(successAlert);

                        // Remove success message after 5 seconds
                        setTimeout(() => {
                            successAlert.remove();
                        }, 5000);

                        // Redirect to home page after a short delay
                        setTimeout(() => {
                            window.location.href = '/';
                        }, 1000);
                    }
                } catch (e) {
                    console.error('Failed to parse JSON:', e);
                    console.log('Raw response was:', text);
                    displayError(form, 'Server returned invalid response');
                }
            } catch (error) {
                console.error('Error in form submission:', error);
                console.log('Error details:', {
                    name: error.name,
                    message: error.message,
                    stack: error.stack
                });
                displayError(form, 'An error occurred. Please try again.');
            } finally {
                // Restore submit button state
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
                console.log('=== FORM SUBMISSION END ===');
            }
        }
    });

    // Setup modal focus and inert management
    [loginModal, registerModal].forEach(modal => {
        if (!modal) return;

        // Handle modal show event
        modal.addEventListener('show.bs.modal', () => {
            setModalInert(modal, false);
        });

        // Handle modal hide event
        modal.addEventListener('hide.bs.modal', () => {
            setModalInert(modal, true);
            // Remove focus from active element
            if (document.activeElement instanceof HTMLElement) {
                document.activeElement.blur();
            }
        });
    });

    // Handle forgot password link click
    document.addEventListener('click', function (e) {
        if (e.target.matches('.forgot-password-link')) {
            e.preventDefault();
            if (emailModal && emailModalInstance) {
                emailModalInstance.show();
            }
        }
    });

    // Load password reset form when modal is shown
    if (emailModal) {
        emailModal.addEventListener('show.bs.modal', async function () {
            try {
                const response = await csrfFetch('/accounts/password-reset/');
                if (!response.ok) {
                    const data = await response.json();
                    throw new Error(data.message || 'Failed to load password reset form');
                }

                const data = await response.json();
                if (data.status === 'success' && data.html) {
                    emailModal.querySelector('.modal-content').innerHTML = data.html;

                    // Add event listener for close button after content is loaded
                    const closeButton = emailModal.querySelector('.btn-close');
                    if (closeButton) {
                        closeButton.addEventListener('click', function () {
                            if (emailModalInstance) {
                                emailModalInstance.hide();
                            }
                        });
                    }
                } else {
                    throw new Error(data.message || 'Failed to load password reset form');
                }
            } catch (error) {
                console.error('Error loading password reset form:', error);
                const errorContainer = emailModal.querySelector('.modal-content');
                if (errorContainer) {
                    errorContainer.innerHTML = `
                        <div class="modal-header">
                            <h5 class="modal-title">Error</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <div class="alert alert-danger">
                                ${error.message || 'Failed to load password reset form. Please try again.'}
                            </div>
                        </div>
                    `;
                }
            }
        });

        // Add event listener for modal hide
        emailModal.addEventListener('hide.bs.modal', function () {
            // Remove focus from active element
            if (document.activeElement instanceof HTMLElement) {
                document.activeElement.blur();
            }
            // Set focus to the main content
            const mainContent = document.querySelector('.main-content');
            if (mainContent) {
                mainContent.focus();
            }
        });
    }

    // Handle password reset form submission
    document.addEventListener('submit', async function (e) {
        if (e.target.classList.contains('password-reset-form')) {
            e.preventDefault();
            const form = e.target;
            const submitButton = form.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;

            try {
                submitButton.disabled = true;
                submitButton.innerHTML = 'Processing...';

                // Get reCAPTCHA token
                const recaptchaToken = document.getElementById('reset_recaptchaResponse').value;
                if (!recaptchaToken) {
                    throw new Error('Please complete the reCAPTCHA verification');
                }

                const formData = new FormData(form);
                formData.append('g-recaptcha-response', recaptchaToken);

                const response = await csrfFetch(form.action, {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                if (response.ok && data.status === 'success') {
                    // Show verification modal
                    const emailModal = document.getElementById('emailModal');
                    const verifyModal = document.getElementById('verifyModal');

                    if (emailModal && verifyModal) {
                        const emailModalInstance = bootstrap.Modal.getInstance(emailModal);
                        const verifyModalInstance = new bootstrap.Modal(verifyModal);

                        // Load verification form content
                        const verifyResponse = await csrfFetch('/accounts/password-reset/verify/');
                        if (!verifyResponse.ok) throw new Error('Failed to load verification form');
                        const verifyHtml = await verifyResponse.text();
                        verifyModal.querySelector('.modal-content').innerHTML = verifyHtml;

                        // Add email to the verification form
                        const emailInput = verifyModal.querySelector('input[name="email"]');
                        if (emailInput) {
                            emailInput.value = formData.get('email');
                        }

                        emailModalInstance.hide();
                        verifyModalInstance.show();
                    }
                } else {
                    // Display error message using displayError function
                    displayError(form, data.message || 'An error occurred. Please try again.');
                }
            } catch (error) {
                console.error('Error in password reset:', error);
                displayError(form, error.message || 'An error occurred. Please try again.');
            } finally {
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
            }
        }
    });

    // Handle verification code form submission
    document.addEventListener('submit', async function (e) {
        if (e.target.classList.contains('verify-form')) {
            e.preventDefault();
            const form = e.target;
            const submitButton = form.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;

            try {
                submitButton.disabled = true;
                submitButton.innerHTML = 'Processing...';

                const formData = new FormData(form);
                const response = await csrfFetch(form.action, {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                console.log('Verification response:', data);

                if (data.status === 'success') {
                    // Show set password modal
                    const verifyModal = document.getElementById('verifyModal');
                    const setPasswordModal = document.getElementById('setPasswordModal');

                    if (verifyModal && setPasswordModal) {
                        const verifyModalInstance = bootstrap.Modal.getInstance(verifyModal);
                        const setPasswordModalInstance = new bootstrap.Modal(setPasswordModal);

                        // Load set password form first
                        const setPasswordResponse = await csrfFetch('/accounts/password-reset/confirm/');
                        if (!setPasswordResponse.ok) throw new Error('Failed to load set password form');
                        const setPasswordData = await setPasswordResponse.json();
                        console.log('Set password response:', setPasswordData);

                        if (setPasswordData.status === 'success' && setPasswordData.html) {
                            setPasswordModal.querySelector('.modal-content').innerHTML = setPasswordData.html;

                            // Wait for the DOM to update
                            await new Promise(resolve => setTimeout(resolve, 100));

                            // Now set the values
                            const emailInput = setPasswordModal.querySelector('input[name="email"]');
                            const tokenInput = setPasswordModal.querySelector('input[name="token"]');
                            const usernameInput = setPasswordModal.querySelector('input[name="username"]');

                            if (emailInput && tokenInput && usernameInput) {
                                console.log('Setting form values:', {
                                    email: data.email,
                                    token: data.token
                                });
                                emailInput.value = data.email;
                                tokenInput.value = data.token;
                                usernameInput.value = data.email;
                            } else {
                                console.error('Form inputs not found:', {
                                    emailInput: !!emailInput,
                                    tokenInput: !!tokenInput,
                                    usernameInput: !!usernameInput
                                });
                                throw new Error('Failed to initialize password reset form');
                            }

                            verifyModalInstance.hide();
                            setPasswordModalInstance.show();
                        } else {
                            throw new Error(setPasswordData.message || 'Failed to load password reset form');
                        }
                    }
                } else {
                    const errorContainer = form.querySelector('#verifyErrorContainer');
                    if (errorContainer) {
                        errorContainer.innerHTML = `<div class="alert alert-danger">${data.message}</div>`;
                    }
                }
            } catch (error) {
                console.error('Error in verification:', error);
                const errorContainer = form.querySelector('#verifyErrorContainer');
                if (errorContainer) {
                    errorContainer.innerHTML = `<div class="alert alert-danger">${error.message || 'An error occurred. Please try again.'}</div>`;
                }
            } finally {
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
            }
        }
    });

    // Handle set password form submission
    document.addEventListener('submit', async function (e) {
        if (e.target.classList.contains('set-password-form')) {
            e.preventDefault();
            const form = e.target;
            const submitButton = form.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;

            try {
                submitButton.disabled = true;
                submitButton.innerHTML = 'Processing...';

                const formData = new FormData(form);

                // Get email and token from hidden fields
                const email = formData.get('email');
                const token = formData.get('token');

                if (!email || !token) {
                    throw new Error('Missing required fields');
                }

                const response = await csrfFetch(form.action, {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.status === 'success') {
                    // Show success message and close modal
                    const setPasswordModal = document.getElementById('setPasswordModal');
                    if (setPasswordModal) {
                        const setPasswordModalInstance = bootstrap.Modal.getInstance(setPasswordModal);
                        setPasswordModalInstance.hide();
                    }

                    // Show success message
                    const successAlert = document.createElement('div');
                    successAlert.className = 'alert alert-success';
                    successAlert.innerHTML = data.message || 'Your password has been reset successfully. You can now login with your new password.';
                    document.querySelector('.main-content .container').prepend(successAlert);

                    // Remove success message after 5 seconds
                    setTimeout(() => {
                        successAlert.remove();
                    }, 5000);

                    // Redirect to login page after a short delay
                    setTimeout(() => {
                        window.location.href = '/accounts/login/';
                    }, 1000);
                } else {
                    const errorContainer = form.querySelector('#passwordErrorContainer');
                    if (errorContainer) {
                        errorContainer.innerHTML = `<div class="alert alert-danger">${data.message}</div>`;
                    }
                }
            } catch (error) {
                console.error('Error in setting password:', error);
                const errorContainer = form.querySelector('#passwordErrorContainer');
                if (errorContainer) {
                    errorContainer.innerHTML = `<div class="alert alert-danger">${error.message || 'An error occurred. Please try again.'}</div>`;
                }
            } finally {
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
            }
        }
    });

    // Initialize password reset modals
    [emailModal, verifyModal, setPasswordModal].forEach(modal => {
        if (modal) {
            modal.addEventListener('shown.bs.modal', function () {
                enableButtonsAndGetTokens();
            });
        }
    });
});

function handlePasswordResetResponse(response) {
    if (response.status === 'success') {
        // Show success message
        showMessage(response.message, 'success');

        // If there's a redirect URL, navigate to it
        if (response.redirect) {
            window.location.href = response.redirect;
        } else {
            // Otherwise close the modal and reload the page
            const modal = bootstrap.Modal.getInstance(document.getElementById('emailModal'));
            if (modal) {
                modal.hide();
            }
            window.location.reload();
        }
    } else {
        showMessage(response.message, 'error');
    }
}
