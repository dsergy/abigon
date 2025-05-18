console.log("=== AUTH.JS LOADED ===");

// Helper for safe fetch requests with CSRF token
const csrfFetch = (url, options = {}) => {
    console.log("CSRF Fetch called with URL:", url);
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
            'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin'
    };

    return fetch(url, { ...defaultOptions, ...options });
};

// Helper for safe Bootstrap modal instance management
const getOrCreateModal = (element) => {
    console.log('Getting or creating modal for element:', element);
    if (!element) {
        console.error('Modal element not found');
        return null;
    }
    const modal = bootstrap.Modal.getOrCreateInstance(element);
    console.log('Modal instance:', modal);
    return modal;
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
    console.log('=== ERROR HANDLING START ===');
    console.log('Error message:', message);
    console.log('Form element:', form);

    if (!form) {
        console.error('Form not found');
        return;
    }

    // Create error message element
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger';
    errorDiv.textContent = message;
    console.log('Created error div:', errorDiv);

    // Find error container in modal content
    const modalContent = form.closest('.modal-content');
    console.log('Modal content:', modalContent);

    let errorContainer = modalContent.querySelector('#registerErrorContainer');
    console.log('Found error container:', errorContainer);

    if (!errorContainer) {
        console.log('Creating new error container');
        errorContainer = document.createElement('div');
        errorContainer.id = 'registerErrorContainer';
        const modalBody = modalContent.querySelector('.modal-body');
        if (modalBody) {
            modalBody.insertBefore(errorContainer, form);
            console.log('Inserted container into modal body');
        } else {
            modalContent.insertBefore(errorContainer, form);
            console.log('Inserted container into modal content');
        }
    }

    // Clear existing errors and add new one
    errorContainer.innerHTML = '';
    errorContainer.appendChild(errorDiv);
    console.log('Added error message to container');

    // Scroll to error message
    errorContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    console.log('=== ERROR HANDLING END ===');
}

// Main initialization when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    console.log('=== DOM LOADED ===');
    console.log('Document body:', document.body.innerHTML);

    // Get modal elements
    const loginModal = document.getElementById('loginModal');
    const registerModal = document.getElementById('registerModal');

    console.log('Login modal element:', loginModal);
    console.log('Register modal element:', registerModal);

    // Initialize modals
    let loginModalInstance;
    let registerModalInstance;

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
            console.log('Login modal instance:', loginModalInstance);
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
            console.log('Register modal instance:', registerModalInstance);
        } catch (error) {
            console.error('Error creating register modal instance:', error);
        }
    }

    // Function to handle login click
    function handleLoginClick(e) {
        console.log('Login click handler called');
        console.log('Event target:', e.target);
        console.log('Event current target:', e.currentTarget);

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
        console.log('Fetching login form content...');
        csrfFetch('/accounts/login/modal/')
            .then(response => {
                console.log('Login form response status:', response.status);
                if (!response.ok) throw new Error('Failed to load login form');
                return response.text();
            })
            .then(html => {
                console.log('Login form HTML received');
                const modalContent = loginModal.querySelector('.modal-content');
                if (modalContent) {
                    modalContent.innerHTML = html;
                    console.log('Modal content updated successfully');
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
            console.log('Login link found, calling handler');
            handleLoginClick(e);
        }
    });

    // Also try direct event listener on the button
    const loginButton = document.getElementById('loginButton');
    if (loginButton) {
        console.log('Found login button, adding direct click handler');
        loginButton.addEventListener('click', handleLoginClick);
    } else {
        console.log('Login button not found by ID');
    }

    // Remove the show.bs.modal event listener since we're handling content loading in the click handler
    loginModal.removeEventListener('show.bs.modal', async function () {
        // ... existing code ...
    });

    // Load registration form when modal is shown
    registerModal.addEventListener('show.bs.modal', async function () {
        try {
            console.log('Loading registration form...');
            const response = await csrfFetch('/accounts/register/modal/');
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
});
