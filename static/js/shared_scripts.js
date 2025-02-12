// Alert Animation Functions
function fadeOutAlert(alertElement) {
    if (!alertElement) return;
    
    alertElement.classList.add('fade-out');
    setTimeout(() => {
        alertElement.style.display = 'none';
        alertElement.remove();
    }, 300); // Match the transition duration
}

function showAlert(message, type = 'info', duration = 5000) {
    const alertContainer = document.querySelector('.alert-container') || createAlertContainer();
    const alert = createAlertElement(message, type);
    alertContainer.appendChild(alert);
    
    // Trigger reflow to ensure animation plays
    alert.offsetHeight;
    alert.classList.add('fade-in');
    
    // Auto dismiss after duration
    setTimeout(() => {
        fadeOutAlert(alert);
    }, duration);
}

function createAlertContainer() {
    const container = document.createElement('div');
    container.className = 'alert-container';
    document.body.appendChild(container);
    return container;
}

function createAlertElement(message, type) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.setAttribute('role', 'alert');
    
    const closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.className = 'btn-close';
    closeButton.setAttribute('data-bs-dismiss', 'alert');
    closeButton.setAttribute('aria-label', 'Close');
    closeButton.onclick = () => fadeOutAlert(alert);
    
    alert.innerHTML = `<strong></strong> ${message}`;
    alert.appendChild(closeButton);
    
    return alert;
}

// Enhanced Form Validation
function validateForm(form) {
    const inputs = form.querySelectorAll('input, select, textarea');
    let isValid = true;
    
    inputs.forEach(input => {
        if (input.hasAttribute('required') && !input.value.trim()) {
            showAlert(`${input.name || 'Field'} is required`, 'danger');
            isValid = false;
            input.classList.add('is-invalid');
        } else if (input.type === 'email' && input.value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(input.value)) {
                showAlert('Please enter a valid email address', 'danger');
                isValid = false;
                input.classList.add('is-invalid');
            }
        } else if (input.type === 'tel' && input.value) {
            const phoneRegex = /^[0-9]{10}$/;
            if (!phoneRegex.test(input.value)) {
                showAlert('Please enter a valid 10-digit phone number', 'danger');
                isValid = false;
                input.classList.add('is-invalid');
            }
        }
    });
    
    return isValid;
}

// Enhanced Password Validation
function validatePassword(password) {
    const requirements = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        lowercase: /[a-z]/.test(password),
        number: /[0-9]/.test(password),
        special: /[!@#$%^&*]/.test(password)
    };
    
    return requirements;
}

function updatePasswordRequirements(password) {
    const requirements = validatePassword(password);
    const elements = {
        length: document.getElementById('length-check'),
        upper: document.getElementById('upper-check'),
        lower: document.getElementById('lower-check'),
        number: document.getElementById('number-check'),
        special: document.getElementById('special-check')
    };
    
    for (const [key, element] of Object.entries(elements)) {
        if (element) {
            element.innerHTML = `${requirements[key] ? '✅' : '❌'} ${element.textContent.substring(2)}`;
            element.style.color = requirements[key] ? '#28a745' : '#dc3545';
        }
    }
    
    return Object.values(requirements).every(Boolean);
}

// Enhanced Scroll Behavior
function smoothScroll(target, duration = 500) {
    const targetPosition = target.getBoundingClientRect().top + window.pageYOffset;
    const startPosition = window.pageYOffset;
    const distance = targetPosition - startPosition;
    let startTime = null;
    
    function animation(currentTime) {
        if (startTime === null) startTime = currentTime;
        const timeElapsed = currentTime - startTime;
        const run = ease(timeElapsed, startPosition, distance, duration);
        window.scrollTo(0, run);
        if (timeElapsed < duration) requestAnimationFrame(animation);
    }
    
    function ease(t, b, c, d) {
        t /= d / 2;
        if (t < 1) return c / 2 * t * t + b;
        t--;
        return -c / 2 * (t * (t - 2) - 1) + b;
    }
    
    requestAnimationFrame(animation);
}

// Enhanced Loading States
function setLoadingState(element, isLoading) {
    if (isLoading) {
        element.disabled = true;
        element.dataset.originalText = element.innerHTML;
        element.innerHTML = '<span class="loading-spinner"></span> Loading...';
    } else {
        element.disabled = false;
        element.innerHTML = element.dataset.originalText;
    }
}

// Enhanced Modal Handling
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        // Add animation classes
        modal.querySelector('.modal-dialog').classList.add('fade-in');
    }
}

// Enhanced Table Sorting
function sortTable(table, column, type = 'string') {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const header = table.querySelector('th:nth-child(' + (column + 1) + ')');
    const isAsc = header.classList.contains('asc');
    
    // Remove sort classes from all headers
    table.querySelectorAll('th').forEach(th => th.classList.remove('asc', 'desc'));
    
    // Add sort class to current header
    header.classList.add(isAsc ? 'desc' : 'asc');
    
    // Sort rows
    rows.sort((a, b) => {
        const aValue = a.cells[column].textContent.trim();
        const bValue = b.cells[column].textContent.trim();
        
        if (type === 'number') {
            return isAsc ? bValue - aValue : aValue - bValue;
        } else if (type === 'date') {
            return isAsc ? new Date(bValue) - new Date(aValue) : new Date(aValue) - new Date(bValue);
        } else {
            return isAsc ? bValue.localeCompare(aValue) : aValue.localeCompare(bValue);
        }
    });
    
    // Reorder rows
    rows.forEach(row => tbody.appendChild(row));
}

// Enhanced Image Loading
function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.add('fade-in');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Enhanced Form Input Handling
function enhanceFormInputs() {
    const inputs = document.querySelectorAll('.form-control, .form-select');
    
    inputs.forEach(input => {
        // Add floating label behavior
        if (input.value) {
            input.classList.add('has-value');
        }
        
        input.addEventListener('focus', () => {
            input.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', () => {
            input.parentElement.classList.remove('focused');
            if (input.value) {
                input.classList.add('has-value');
            } else {
                input.classList.remove('has-value');
            }
        });
        
        // Add character counter for textareas
        if (input.tagName === 'TEXTAREA' && input.hasAttribute('maxlength')) {
            const counter = document.createElement('small');
            counter.className = 'character-counter text-muted';
            counter.textContent = `${input.value.length}/${input.maxLength}`;
            input.parentElement.appendChild(counter);
            
            input.addEventListener('input', () => {
                counter.textContent = `${input.value.length}/${input.maxLength}`;
                if (input.value.length >= input.maxLength) {
                    counter.classList.add('text-danger');
                } else {
                    counter.classList.remove('text-danger');
                }
            });
        }
    });
}

// Enhanced Mobile Menu
function enhanceMobileMenu() {
    const menuToggle = document.querySelector('.mobile-nav-toggle');
    const navMenu = document.querySelector('.navmenu');
    
    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            menuToggle.classList.toggle('bi-list');
            menuToggle.classList.toggle('bi-x');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!navMenu.contains(e.target) && !menuToggle.contains(e.target)) {
                navMenu.classList.remove('active');
                menuToggle.classList.add('bi-list');
                menuToggle.classList.remove('bi-x');
            }
        });
    }
}

// Initialize all enhancements
document.addEventListener('DOMContentLoaded', function() {
    // Initialize alerts
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => fadeOutAlert(alert), 5000);
    });
    
    // Initialize form validation
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', (e) => {
            if (!validateForm(form)) {
                e.preventDefault();
            }
        });
    });
    
    // Initialize password validation
    const passwordInput = document.querySelector('input[type="password"]');
    if (passwordInput) {
        passwordInput.addEventListener('input', (e) => {
            updatePasswordRequirements(e.target.value);
        });
    }
    
    // Initialize smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.querySelector(anchor.getAttribute('href'));
            if (target) smoothScroll(target);
        });
    });
    
    // Initialize lazy loading
    lazyLoadImages();
    
    // Initialize form enhancements
    enhanceFormInputs();
    
    // Initialize mobile menu
    enhanceMobileMenu();
    
    // Add scroll to top button behavior
    const scrollTopBtn = document.getElementById('scroll-top');
    if (scrollTopBtn) {
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 300) {
                scrollTopBtn.classList.add('show');
            } else {
                scrollTopBtn.classList.remove('show');
            }
        });
        
        scrollTopBtn.addEventListener('click', (e) => {
            e.preventDefault();
            smoothScroll(document.documentElement);
        });
    }
    
    // Add table sorting
    document.querySelectorAll('table[data-sortable]').forEach(table => {
        table.querySelectorAll('th').forEach((header, index) => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                const type = header.dataset.type || 'string';
                sortTable(table, index, type);
            });
        });
    });
}); 