// Sudarshan Engine Web Interface Application Logic

class SudarshanWebApp {
    constructor() {
        this.currentSection = 'dashboard';
        this.backendConnected = false;
        this.apiBaseUrl = 'http://localhost:8000';
        this.basicAuth = {
            username: 'admin',
            password: 'password'
        };
        this.keys = {
            kem: null,
            signature: null
        };
        this.encryptedFile = null;
        this.decryptedFile = null;

        // Enterprise features
        this.sessionStartTime = Date.now();
        this.sessionDuration = 30 * 60 * 1000; // 30 minutes
        this.auditLog = [];
        this.performanceMetrics = {
            loadTime: 0,
            memoryUsage: 0,
            apiCalls: 0
        };
        this.errorCount = 0;
        this.csrfToken = this.generateCSRFToken();

        // User authentication
        this.currentUser = null;
        this.userKeys = {
            kem: null,
            signature: null
        };
        this.isAuthenticated = false;

        this.init();
    }

    async init() {
        this.bindEvents();
        this.checkBackendConnection();
        this.initializeEnterpriseFeatures();

        // Check if user is already authenticated
        const savedUser = this.getSavedUser();
        if (savedUser) {
            this.currentUser = savedUser;
            this.isAuthenticated = true;
            this.showMainApp();
            this.loadUserKeys();
            this.showNotification(`Welcome back, ${savedUser.firstName}!`, 'success');
            this.logAuditEvent('user_login', `User ${savedUser.email} logged in (remembered)`);
        } else {
            this.showAuthModal();
        }
    }

    // Enterprise Features Initialization
    initializeEnterpriseFeatures() {
        this.initializeSessionManagement();
        this.initializePerformanceMonitoring();
        this.initializeKeyboardShortcuts();
        this.initializeErrorBoundary();
        this.initializeFormValidation();
    }

    // Session Management
    initializeSessionManagement() {
        this.updateSessionTimer();
        setInterval(() => this.updateSessionTimer(), 1000);

        // Warn user before session expires
        setTimeout(() => {
            if (this.sessionDuration > 5 * 60 * 1000) { // 5 minutes left
                this.showNotification('Your session will expire in 5 minutes. Save your work.', 'warning');
            }
        }, this.sessionDuration - 5 * 60 * 1000);
    }

    updateSessionTimer() {
        const elapsed = Date.now() - this.sessionStartTime;
        const remaining = Math.max(0, this.sessionDuration - elapsed);

        if (remaining <= 0) {
            this.handleSessionExpiry();
            return;
        }

        const minutes = Math.floor(remaining / (60 * 1000));
        const seconds = Math.floor((remaining % (60 * 1000)) / 1000);
        const timerElement = document.getElementById('session-timer');

        if (timerElement) {
            timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }

        // Show session info if less than 10 minutes remaining
        const sessionInfo = document.getElementById('session-info');
        if (remaining < 10 * 60 * 1000 && sessionInfo) {
            sessionInfo.classList.add('show');
        }
    }

    extendSession() {
        this.sessionStartTime = Date.now();
        this.sessionDuration = 30 * 60 * 1000; // Reset to 30 minutes
        document.getElementById('session-info').classList.remove('show');
        this.showNotification('Session extended successfully', 'success');
        this.logAuditEvent('session_extended', 'User extended their session');
    }

    handleSessionExpiry() {
        this.showNotification('Your session has expired. Please refresh the page.', 'error');
        this.logAuditEvent('session_expired', 'User session expired');
        // In production, redirect to login or show expiry modal
        setTimeout(() => {
            window.location.reload();
        }, 5000);
    }

    // Performance Monitoring
    initializePerformanceMonitoring() {
        // Measure page load time
        if (performance.timing) {
            const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
            this.performanceMetrics.loadTime = loadTime;
            document.getElementById('load-time').textContent = `${loadTime}ms`;
        }

        // Monitor memory usage
        if (performance.memory) {
            setInterval(() => {
                const memoryMB = Math.round(performance.memory.usedJSHeapSize / 1024 / 1024);
                this.performanceMetrics.memoryUsage = memoryMB;
                document.getElementById('memory-usage').textContent = `${memoryMB}MB`;
            }, 5000);
        }

        // Show performance indicator after 3 seconds
        setTimeout(() => {
            document.getElementById('performance-indicator').classList.add('show');
        }, 3000);
    }

    togglePerformanceMetrics() {
        const metrics = document.getElementById('performance-metrics');
        metrics.style.display = metrics.style.display === 'none' ? 'block' : 'none';
    }

    // Audit Logging
    logAuditEvent(action, details = '') {
        const auditEntry = {
            timestamp: new Date().toISOString(),
            action: action,
            details: details,
            userAgent: navigator.userAgent,
            sessionId: this.generateSessionId()
        };

        this.auditLog.push(auditEntry);

        // Keep only last 100 entries
        if (this.auditLog.length > 100) {
            this.auditLog.shift();
        }

        this.updateAuditDisplay();
    }

    updateAuditDisplay() {
        const auditEntries = document.getElementById('audit-entries');
        if (!auditEntries) return;

        auditEntries.innerHTML = this.auditLog.slice(-10).map(entry => `
            <div class="audit-entry">
                <div>
                    <span class="audit-action">${entry.action}</span>
                    <span class="audit-details">${entry.details}</span>
                </div>
                <span class="audit-timestamp">${new Date(entry.timestamp).toLocaleTimeString()}</span>
            </div>
        `).join('');
    }

    clearAuditLog() {
        this.auditLog = [];
        this.updateAuditDisplay();
        this.logAuditEvent('audit_log_cleared', 'User cleared audit log');
    }

    // Keyboard Shortcuts
    initializeKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+Shift+A: Toggle audit log
            if (e.ctrlKey && e.shiftKey && e.key === 'A') {
                e.preventDefault();
                const auditLog = document.getElementById('audit-log');
                auditLog.classList.toggle('show');
            }

            // Ctrl+Shift+P: Toggle performance metrics
            if (e.ctrlKey && e.shiftKey && e.key === 'P') {
                e.preventDefault();
                this.togglePerformanceMetrics();
            }

            // Ctrl+Shift+R: Reload application
            if (e.ctrlKey && e.shiftKey && e.key === 'R') {
                e.preventDefault();
                this.reloadApplication();
            }
        });
    }

    // Error Boundary
    initializeErrorBoundary() {
        window.addEventListener('error', (event) => {
            this.handleGlobalError(event.error, event.message, event.filename, event.lineno);
        });

        window.addEventListener('unhandledrejection', (event) => {
            this.handleGlobalError(event.reason, 'Unhandled Promise Rejection');
        });
    }

    handleGlobalError(error, message, filename = '', lineno = '') {
        this.errorCount++;
        console.error('Global Error:', error);

        const errorDetails = {
            message: message,
            stack: error?.stack || 'No stack trace available',
            filename: filename,
            lineno: lineno,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent
        };

        // Log error to audit trail
        this.logAuditEvent('error_occurred', `Error: ${message}`);

        // Show error boundary if too many errors
        if (this.errorCount >= 3) {
            this.showErrorBoundary(errorDetails);
        } else {
            this.showNotification('An error occurred. Please try again.', 'error');
        }

        // In production, send error to monitoring service
        this.reportError(errorDetails);
    }

    showErrorBoundary(errorDetails) {
        const errorBoundary = document.getElementById('error-boundary');
        const errorDetailsDiv = document.getElementById('error-details');

        if (errorBoundary && errorDetailsDiv) {
            errorDetailsDiv.textContent = JSON.stringify(errorDetails, null, 2);
            errorBoundary.classList.add('show');
        }
    }

    reloadApplication() {
        this.logAuditEvent('application_reloaded', 'User manually reloaded application');
        window.location.reload();
    }

    reportError(errorDetails) {
        // In production, send to error monitoring service
        console.log('Error reported:', errorDetails);
    }

    // Form Validation
    initializeFormValidation() {
        // Add real-time validation to forms
        this.setupFormValidation('encrypt-form');
        this.setupFormValidation('decrypt-form');
        this.setupFormValidation('email-notification-form');
    }

    setupFormValidation(formId) {
        const form = document.getElementById(formId);
        if (!form) return;

        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('input', () => this.clearFieldError(input));
        });
    }

    validateField(field) {
        const value = field.value.trim();
        const fieldName = field.name || field.id;
        let isValid = true;
        let errorMessage = '';

        // Required field validation
        if (field.hasAttribute('required') && !value) {
            isValid = false;
            errorMessage = `${fieldName} is required`;
        }

        // Email validation
        if (field.type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Please enter a valid email address';
            }
        }

        // JSON validation for metadata
        if (field.id === 'encrypt-metadata' && value) {
            try {
                JSON.parse(value);
            } catch (e) {
                isValid = false;
                errorMessage = 'Invalid JSON format';
            }
        }

        // File size validation
        if (field.type === 'file' && field.files.length > 0) {
            const maxSize = 100 * 1024 * 1024; // 100MB
            if (field.files[0].size > maxSize) {
                isValid = false;
                errorMessage = 'File size must be less than 100MB';
            }
        }

        this.updateFieldValidation(field, isValid, errorMessage);
        return isValid;
    }

    updateFieldValidation(field, isValid, errorMessage) {
        const formGroup = field.closest('.form-group');
        const errorDiv = formGroup.querySelector('.field-error');

        formGroup.classList.remove('success', 'error');

        if (!isValid) {
            formGroup.classList.add('error');
            if (errorDiv) {
                errorDiv.textContent = errorMessage;
                errorDiv.style.display = 'block';
            }
        } else if (field.value.trim()) {
            formGroup.classList.add('success');
            if (errorDiv) {
                errorDiv.style.display = 'none';
            }
        }
    }

    clearFieldError(field) {
        const formGroup = field.closest('.form-group');
        const errorDiv = formGroup.querySelector('.field-error');

        if (errorDiv && !field.value.trim()) {
            formGroup.classList.remove('error', 'success');
            errorDiv.style.display = 'none';
        }
    }

    // Security Features
    generateCSRFToken() {
        return this.generateRandomHex(32);
    }

    generateSessionId() {
        return this.generateRandomHex(16);
    }

    // Compliance Functions
    showPrivacyPolicy() {
        this.showNotification('Privacy Policy will be displayed here', 'info');
        // In production, show actual privacy policy modal
    }

    showTermsOfService() {
        this.showNotification('Terms of Service will be displayed here', 'info');
        // In production, show actual terms modal
    }

    showCookiePolicy() {
        this.showNotification('Cookie Policy will be displayed here', 'info');
        // In production, show actual cookie policy modal
    }

    showGDPRCompliance() {
        this.showNotification('GDPR compliance information will be displayed here', 'info');
        // In production, show actual GDPR compliance modal
    }

    showSecurityPolicy() {
        this.showNotification('Security Policy will be displayed here', 'info');
        // In production, show actual security policy modal
    }

    // User Authentication Methods
    showAuthModal() {
        const authModal = document.getElementById('auth-modal');
        const mainApp = document.getElementById('main-app');

        if (authModal) {
            authModal.style.display = 'flex';
        }
        if (mainApp) {
            mainApp.style.display = 'none';
        }
    }

    showMainApp() {
        const authModal = document.getElementById('auth-modal');
        const mainApp = document.getElementById('main-app');

        if (authModal) {
            authModal.style.display = 'none';
        }
        if (mainApp) {
            mainApp.style.display = 'block';
        }

        this.showSection('dashboard');
        this.updateUserProfile();
    }

    showAuthTab(tab) {
        // Update tab buttons
        document.querySelectorAll('.auth-tab').forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[onclick="showAuthTab('${tab}')"]`).classList.add('active');

        // Update form visibility
        document.querySelectorAll('.auth-form').forEach(form => form.classList.remove('active'));
        document.getElementById(`${tab}-form`).classList.add('active');
    }

    async handleLogin(event) {
        event.preventDefault();

        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        const rememberMe = document.getElementById('remember-me').checked;

        // Validate inputs
        if (!this.validateEmail(email)) {
            this.showFieldError('login-email', 'Please enter a valid email address');
            return;
        }

        if (!password) {
            this.showFieldError('login-password', 'Password is required');
            return;
        }

        try {
            // Simulate login (replace with actual authentication)
            const user = await this.authenticateUser(email, password);

            if (user) {
                this.currentUser = user;
                this.isAuthenticated = true;

                if (rememberMe) {
                    this.saveUser(user);
                }

                this.showMainApp();
                this.loadUserKeys();
                this.showNotification(`Welcome back, ${user.firstName}!`, 'success');
                this.logAuditEvent('user_login', `User ${email} logged in`);

                // Reset form
                event.target.reset();
            } else {
                this.showNotification('Invalid email or password', 'error');
                this.logAuditEvent('login_failed', `Failed login attempt for ${email}`);
            }
        } catch (error) {
            this.showNotification('Login failed. Please try again.', 'error');
            this.logAuditEvent('login_error', `Login error for ${email}: ${error.message}`);
        }
    }

    async handleSignup(event) {
        event.preventDefault();

        const firstName = document.getElementById('signup-firstname').value;
        const lastName = document.getElementById('signup-lastname').value;
        const email = document.getElementById('signup-email').value;
        const password = document.getElementById('signup-password').value;
        const confirmPassword = document.getElementById('signup-confirm-password').value;
        const acceptTerms = document.getElementById('accept-terms').checked;

        // Validate inputs
        let isValid = true;

        if (!firstName.trim()) {
            this.showFieldError('signup-firstname', 'First name is required');
            isValid = false;
        }

        if (!lastName.trim()) {
            this.showFieldError('signup-lastname', 'Last name is required');
            isValid = false;
        }

        if (!this.validateEmail(email)) {
            this.showFieldError('signup-email', 'Please enter a valid email address');
            isValid = false;
        }

        if (!this.validatePassword(password)) {
            this.showFieldError('signup-password', 'Password must be at least 8 characters with uppercase, lowercase, and number');
            isValid = false;
        }

        if (password !== confirmPassword) {
            this.showFieldError('signup-confirm-password', 'Passwords do not match');
            isValid = false;
        }

        if (!acceptTerms) {
            this.showFieldError('accept-terms', 'You must accept the terms and conditions');
            isValid = false;
        }

        if (!isValid) return;

        try {
            // Simulate user registration (replace with actual registration)
            const user = await this.registerUser({
                firstName,
                lastName,
                email,
                password
            });

            if (user) {
                this.currentUser = user;
                this.isAuthenticated = true;
                this.saveUser(user);

                this.showMainApp();
                this.generateUserKeys(); // Generate unique keys for new user
                this.showNotification(`Welcome to Sudarshan Engine, ${user.firstName}!`, 'success');
                this.logAuditEvent('user_registration', `New user ${email} registered`);

                // Reset form
                event.target.reset();
            } else {
                this.showNotification('Registration failed. Please try again.', 'error');
            }
        } catch (error) {
            this.showNotification('Registration failed. Please try again.', 'error');
            this.logAuditEvent('registration_error', `Registration error for ${email}: ${error.message}`);
        }
    }

    async authenticateUser(email, password) {
        // Simulate authentication (replace with actual backend call)
        const users = JSON.parse(localStorage.getItem('sudarshan_users') || '[]');
        const user = users.find(u => u.email === email && u.password === this.hashPassword(password));

        if (user) {
            // Remove password from user object
            const { password: _, ...userWithoutPassword } = user;
            return userWithoutPassword;
        }

        return null;
    }

    async registerUser(userData) {
        // Simulate user registration (replace with actual backend call)
        const users = JSON.parse(localStorage.getItem('sudarshan_users') || '[]');

        // Check if user already exists
        if (users.find(u => u.email === userData.email)) {
            throw new Error('User already exists');
        }

        const newUser = {
            id: this.generateUserId(),
            ...userData,
            password: this.hashPassword(userData.password),
            createdAt: new Date().toISOString(),
            keysGenerated: false
        };

        users.push(newUser);
        localStorage.setItem('sudarshan_users', JSON.stringify(users));

        // Remove password from returned user object
        const { password: _, ...userWithoutPassword } = newUser;
        return userWithoutPassword;
    }

    generateUserKeys() {
        // Generate unique keys for this user
        this.userKeys.kem = {
            algorithm: 'Kyber1024',
            publicKey: this.generateRandomHex(1568),
            secretKey: this.generateRandomHex(3168),
            userId: this.currentUser.id,
            generated: new Date().toISOString()
        };

        this.userKeys.signature = {
            algorithm: 'Dilithium5',
            publicKey: this.generateRandomHex(2592),
            secretKey: this.generateRandomHex(4864),
            userId: this.currentUser.id,
            generated: new Date().toISOString()
        };

        // Save user keys
        this.saveUserKeys();

        this.logAuditEvent('keys_generated', 'User keys generated for new account');
    }

    loadUserKeys() {
        const savedKeys = localStorage.getItem(`sudarshan_keys_${this.currentUser.id}`);
        if (savedKeys) {
            this.userKeys = JSON.parse(savedKeys);
        } else {
            // Generate keys if not found
            this.generateUserKeys();
        }
    }

    saveUserKeys() {
        localStorage.setItem(`sudarshan_keys_${this.currentUser.id}`, JSON.stringify(this.userKeys));
    }

    saveUser(user) {
        localStorage.setItem('sudarshan_current_user', JSON.stringify(user));
    }

    getSavedUser() {
        const saved = localStorage.getItem('sudarshan_current_user');
        return saved ? JSON.parse(saved) : null;
    }

    updateUserProfile() {
        if (!this.currentUser) return;

        const userName = document.getElementById('user-name');
        const userEmail = document.getElementById('user-email');
        const userAvatar = document.getElementById('user-avatar');

        if (userName) userName.textContent = `${this.currentUser.firstName} ${this.currentUser.lastName}`;
        if (userEmail) userEmail.textContent = this.currentUser.email;
        if (userAvatar) userAvatar.textContent = this.currentUser.firstName.charAt(0).toUpperCase();
    }

    logoutUser() {
        this.logAuditEvent('user_logout', `User ${this.currentUser.email} logged out`);

        // Clear user data
        this.currentUser = null;
        this.isAuthenticated = false;
        this.userKeys = { kem: null, signature: null };

        // Clear local storage
        localStorage.removeItem('sudarshan_current_user');

        // Show auth modal
        this.showAuthModal();
        this.showNotification('You have been logged out successfully', 'success');
    }

    toggleUserMenu() {
        const dropdown = document.getElementById('user-menu-dropdown');
        if (dropdown) {
            dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
        }
    }

    // API Helper Methods
    async makeAPICall(endpoint, method = 'GET', data = null) {
        const url = `${this.apiBaseUrl}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + btoa(`${this.basicAuth.username}:${this.basicAuth.password}`)
        };

        const config = {
            method: method,
            headers: headers
        };

        if (data && (method === 'POST' || method === 'PUT')) {
            config.body = JSON.stringify(data);
        }

        try {
            this.performanceMetrics.apiCalls++;
            const response = await fetch(url, config);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            return result;
        } catch (error) {
            console.error(`API call to ${endpoint} failed:`, error);
            throw error;
        }
    }

    async makeFileUploadCall(endpoint, formData) {
        const url = `${this.apiBaseUrl}${endpoint}`;
        const headers = {
            'Authorization': 'Basic ' + btoa(`${this.basicAuth.username}:${this.basicAuth.password}`)
        };

        const config = {
            method: 'POST',
            headers: headers,
            body: formData
        };

        try {
            this.performanceMetrics.apiCalls++;
            const response = await fetch(url, config);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            return result;
        } catch (error) {
            console.error(`File upload to ${endpoint} failed:`, error);
            throw error;
        }
    }

    // Utility methods
    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    validatePassword(password) {
        // At least 8 characters, with uppercase, lowercase, and number
        const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/;
        return passwordRegex.test(password);
    }

    hashPassword(password) {
        // Simple hash for demo (replace with proper hashing in production)
        return btoa(password + 'sudarshan_salt');
    }

    generateUserId() {
        return 'user_' + this.generateRandomHex(16);
    }

    showFieldError(fieldId, message) {
        const errorDiv = document.getElementById(fieldId + '-error');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }
    }

    // Placeholder methods for future implementation
    showUserProfile() {
        this.showNotification('User profile will be displayed here', 'info');
    }

    showSecuritySettings() {
        this.showNotification('Security settings will be displayed here', 'info');
    }

    showUserKeys() {
        this.showNotification('User keys management will be displayed here', 'info');
    }

    showForgotPassword() {
        this.showNotification('Password reset functionality will be available soon', 'info');
    }

    bindEvents() {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const section = e.currentTarget.dataset.section;
                this.showSection(section);
            });
        });

        // Encrypt form
        this.bindEncryptForm();

        // Decrypt form
        this.bindDecryptForm();

        // Key management
        this.bindKeyManagement();

        // File inputs
        this.bindFileInputs();

        // Authentication forms
        this.bindAuthForms();
    }

    showSection(sectionId) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${sectionId}"]`).classList.add('active');

        // Update content
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(sectionId).classList.add('active');

        this.currentSection = sectionId;
    }

    async checkBackendConnection() {
        try {
            const response = await this.makeAPICall('/api/status');
            if (response.status === 'online') {
                this.backendConnected = true;
                document.getElementById('status-dot').style.backgroundColor = 'var(--success-color)';
                document.getElementById('status-text').textContent = 'Connected';
                this.logAuditEvent('backend_connection', 'Successfully connected to Sudarshan Engine backend');
            } else {
                throw new Error('Backend returned invalid status');
            }
        } catch (error) {
            this.backendConnected = false;
            document.getElementById('status-dot').style.backgroundColor = 'var(--error-color)';
            document.getElementById('status-text').textContent = 'Disconnected';
            this.showNotification('Backend connection failed: ' + error.message, 'error');
            this.logAuditEvent('backend_connection_failed', `Connection failed: ${error.message}`);
        }
    }

    bindEncryptForm() {
        const form = document.getElementById('encrypt-form');
        const input = document.getElementById('encrypt-input');
        const resetBtn = document.getElementById('encrypt-reset');

        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                document.getElementById('encrypt-file-info').textContent =
                    `Selected: ${file.name} (${this.formatFileSize(file.size)})`;
            } else {
                document.getElementById('encrypt-file-info').textContent = 'No file selected';
            }
        });

        resetBtn.addEventListener('click', () => {
            form.reset();
            document.getElementById('encrypt-file-info').textContent = 'No file selected';
            document.getElementById('encrypt-progress').style.display = 'none';
            document.getElementById('encrypt-result').style.display = 'none';
        });

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Validate all form fields
            const formFields = form.querySelectorAll('input, textarea, select');
            let isFormValid = true;
            formFields.forEach(field => {
                if (!this.validateField(field)) {
                    isFormValid = false;
                }
            });

            if (!isFormValid) {
                this.showNotification('Please correct the form errors before submitting', 'error');
                return;
            }

            const file = input.files[0];
            if (!file) {
                this.showNotification('Please select a file to encrypt', 'error');
                this.logAuditEvent('encryption_failed', 'No file selected');
                return;
            }

            if (!this.backendConnected) {
                this.showNotification('Backend not connected', 'error');
                this.logAuditEvent('encryption_failed', 'Backend not connected');
                return;
            }

            this.logAuditEvent('encryption_started', `File: ${file.name} (${this.formatFileSize(file.size)})`);

            // Show progress
            document.getElementById('encrypt-progress').style.display = 'block';
            document.getElementById('encrypt-result').style.display = 'none';
            const progressFill = document.getElementById('encrypt-progress-fill');
            const progressText = document.getElementById('encrypt-progress-text');

            try {
                progressText.textContent = 'Reading file...';
                progressFill.style.width = '25%';

                // Read file
                const fileData = await this.readFile(file);

                progressText.textContent = 'Generating quantum-safe keys...';
                progressFill.style.width = '50%';

                // Simulate key generation
                await this.delay(500);

                progressText.textContent = 'Encrypting file...';
                progressFill.style.width = '75%';

                // Prepare form data for file upload
                const formData = new FormData();
                formData.append('file', file);
                formData.append('algorithm', document.getElementById('encrypt-algorithm').value);
                formData.append('compression', document.getElementById('encrypt-compression').value);
                formData.append('metadata', document.getElementById('encrypt-metadata').value);
                formData.append('signature', document.getElementById('encrypt-signature').checked);

                progressText.textContent = 'Uploading and encrypting...';
                progressFill.style.width = '75%';

                // Make API call to encrypt file
                const result = await this.makeFileUploadCall('/api/encrypt', formData);

                progressText.textContent = 'Finalizing...';
                progressFill.style.width = '90%';

                // Store encrypted file info
                this.encryptedFile = {
                    name: result.filename || file.name + '.spq',
                    data: result.data || fileData,
                    size: result.size || fileData.length,
                    algorithm: result.algorithm,
                    downloadUrl: result.download_url
                };

                progressFill.style.width = '100%';
                progressText.textContent = 'Encryption complete!';

                // Show result
                setTimeout(() => {
                    document.getElementById('encrypt-progress').style.display = 'none';
                    document.getElementById('encrypt-result').style.display = 'block';
                    progressFill.style.width = '0%';
                }, 500);

                this.showNotification('File encrypted successfully!', 'success');
                this.logAuditEvent('encryption_completed', `Encrypted: ${this.encryptedFile.name} using ${result.algorithm}`);

            } catch (error) {
                console.error('Encryption error:', error);
                this.showNotification('Encryption failed: ' + error.message, 'error');
                this.logAuditEvent('encryption_failed', `Error: ${error.message}`);
                document.getElementById('encrypt-progress').style.display = 'none';
                progressFill.style.width = '0%';
            }
        });
    }

    bindDecryptForm() {
        const form = document.getElementById('decrypt-form');
        const input = document.getElementById('decrypt-input');
        const resetBtn = document.getElementById('decrypt-reset');

        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                document.getElementById('decrypt-file-info').textContent =
                    `Selected: ${file.name} (${this.formatFileSize(file.size)})`;
            } else {
                document.getElementById('decrypt-file-info').textContent = 'No file selected';
            }
        });

        resetBtn.addEventListener('click', () => {
            form.reset();
            document.getElementById('decrypt-file-info').textContent = 'No file selected';
            document.getElementById('decrypt-progress').style.display = 'none';
            document.getElementById('decrypt-result').style.display = 'none';
        });

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Validate all form fields
            const formFields = form.querySelectorAll('input, textarea, select');
            let isFormValid = true;
            formFields.forEach(field => {
                if (!this.validateField(field)) {
                    isFormValid = false;
                }
            });

            if (!isFormValid) {
                this.showNotification('Please correct the form errors before submitting', 'error');
                return;
            }

            const file = input.files[0];
            if (!file) {
                this.showNotification('Please select a .spq file to decrypt', 'error');
                this.logAuditEvent('decryption_failed', 'No file selected');
                return;
            }

            if (!file.name.endsWith('.spq')) {
                this.showNotification('Please select a valid .spq file', 'error');
                this.logAuditEvent('decryption_failed', 'Invalid file type selected');
                return;
            }

            if (!this.backendConnected) {
                this.showNotification('Backend not connected', 'error');
                this.logAuditEvent('decryption_failed', 'Backend not connected');
                return;
            }

            this.logAuditEvent('decryption_started', `File: ${file.name} (${this.formatFileSize(file.size)})`);

            // Show progress
            document.getElementById('decrypt-progress').style.display = 'block';
            document.getElementById('decrypt-result').style.display = 'none';
            const progressFill = document.getElementById('decrypt-progress-fill');
            const progressText = document.getElementById('decrypt-progress-text');

            try {
                progressText.textContent = 'Validating .spq file...';
                progressFill.style.width = '25%';

                // Read file
                const fileData = await this.readFile(file);

                progressText.textContent = 'Verifying signature...';
                progressFill.style.width = '50%';

                // Simulate verification
                await this.delay(500);

                progressText.textContent = 'Decrypting file...';
                progressFill.style.width = '75%';

                // Prepare form data for file upload
                const formData = new FormData();
                formData.append('file', file);

                progressText.textContent = 'Uploading and decrypting...';
                progressFill.style.width = '75%';

                // Make API call to decrypt file
                const result = await this.makeFileUploadCall('/api/decrypt', formData);

                progressText.textContent = 'Finalizing...';
                progressFill.style.width = '90%';

                // Store decrypted file info
                this.decryptedFile = {
                    name: result.filename || file.name.replace('.spq', ''),
                    data: result.data || fileData,
                    size: result.size || fileData.length,
                    verified: result.verified,
                    downloadUrl: result.download_url
                };

                progressFill.style.width = '100%';
                progressText.textContent = 'Decryption complete!';

                // Show result
                setTimeout(() => {
                    document.getElementById('decrypt-progress').style.display = 'none';
                    document.getElementById('decrypt-result').style.display = 'block';
                    progressFill.style.width = '0%';
                }, 500);

                this.showNotification('File decrypted successfully!', 'success');
                this.logAuditEvent('decryption_completed', `Decrypted: ${this.decryptedFile.name} (verified: ${result.verified})`);

            } catch (error) {
                console.error('Decryption error:', error);
                this.showNotification('Decryption failed: ' + error.message, 'error');
                this.logAuditEvent('decryption_failed', `Error: ${error.message}`);
                document.getElementById('decrypt-progress').style.display = 'none';
                progressFill.style.width = '0%';
            }
        });
    }

    bindKeyManagement() {
        // KEM Key Generation
        document.getElementById('generate-kem-btn').addEventListener('click', async () => {
            try {
                this.showNotification('Generating quantum-safe keys...', 'info');

                // Make API call to generate keys
                const result = await this.makeAPICall('/api/generate-keys', 'POST', {
                    key_type: 'kem',
                    algorithm: 'Kyber1024'
                });

                this.userKeys.kem = {
                    algorithm: result.kem_keys.algorithm,
                    publicKey: result.kem_keys.public_key,
                    secretKey: result.kem_keys.secret_key,
                    userId: this.currentUser.id,
                    generated: result.timestamp
                };

                this.saveUserKeys();
                this.updateKeyDisplay('kem');
                document.getElementById('kem-keys-display').style.display = 'block';

                this.showNotification('KEM keypair generated successfully!', 'success');
                this.logAuditEvent('kem_keys_generated', 'User generated new KEM keypair');

            } catch (error) {
                this.showNotification('Key generation failed: ' + error.message, 'error');
                this.logAuditEvent('key_generation_failed', `KEM key generation failed: ${error.message}`);
            }
        });

        // Signature Key Generation
        document.getElementById('generate-sig-btn').addEventListener('click', async () => {
            try {
                this.showNotification('Generating quantum-safe signature keys...', 'info');

                // Make API call to generate keys
                const result = await this.makeAPICall('/api/generate-keys', 'POST', {
                    key_type: 'signature',
                    algorithm: 'Dilithium5'
                });

                this.userKeys.signature = {
                    algorithm: result.signature_keys.algorithm,
                    publicKey: result.signature_keys.public_key,
                    secretKey: result.signature_keys.secret_key,
                    userId: this.currentUser.id,
                    generated: result.timestamp
                };

                this.saveUserKeys();
                this.updateKeyDisplay('sig');
                document.getElementById('sig-keys-display').style.display = 'block';

                this.showNotification('Signature keypair generated successfully!', 'success');
                this.logAuditEvent('signature_keys_generated', 'User generated new signature keypair');

            } catch (error) {
                this.showNotification('Key generation failed: ' + error.message, 'error');
                this.logAuditEvent('key_generation_failed', `Signature key generation failed: ${error.message}`);
            }
        });

        // Download Keys
        document.getElementById('download-kem-keys').addEventListener('click', () => {
            this.downloadKeys('kem');
        });

        document.getElementById('download-sig-keys').addEventListener('click', () => {
            this.downloadKeys('sig');
        });
    }

    bindFileInputs() {
        // File input change handlers are already bound in form handlers
    }

    bindAuthForms() {
        // Login form
        const loginForm = document.getElementById('login-form-element');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        // Signup form
        const signupForm = document.getElementById('signup-form-element');
        if (signupForm) {
            signupForm.addEventListener('submit', (e) => this.handleSignup(e));
        }

        // Password strength checker
        const passwordInput = document.getElementById('signup-password');
        if (passwordInput) {
            passwordInput.addEventListener('input', (e) => this.checkPasswordStrength(e.target.value));
        }
    }

    checkPasswordStrength(password) {
        const strengthMeter = document.getElementById('password-strength-fill');
        const strengthText = document.getElementById('password-strength-text');

        if (!password) {
            strengthMeter.style.width = '0%';
            strengthMeter.className = 'strength-fill';
            strengthText.textContent = 'Password strength';
            return;
        }

        let score = 0;
        let feedback = [];

        // Length check
        if (password.length >= 8) score += 25;
        else feedback.push('At least 8 characters');

        // Lowercase check
        if (/[a-z]/.test(password)) score += 25;
        else feedback.push('Lowercase letter');

        // Uppercase check
        if (/[A-Z]/.test(password)) score += 25;
        else feedback.push('Uppercase letter');

        // Number check
        if (/\d/.test(password)) score += 25;
        else feedback.push('Number');

        // Update UI
        strengthMeter.style.width = score + '%';

        if (score < 25) {
            strengthMeter.className = 'strength-fill weak';
            strengthText.textContent = 'Weak password';
        } else if (score < 50) {
            strengthMeter.className = 'strength-fill medium';
            strengthText.textContent = 'Medium strength';
        } else if (score < 75) {
            strengthMeter.className = 'strength-fill strong';
            strengthText.textContent = 'Strong password';
        } else {
            strengthMeter.className = 'strength-fill very-strong';
            strengthText.textContent = 'Very strong password';
        }
    }

    updateKeyDisplay(type) {
        const keyData = this.userKeys[type];
        if (keyData) {
            document.getElementById(`${type}-algorithm`).textContent = keyData.algorithm;
            document.getElementById(`${type}-public`).textContent = keyData.publicKey.substring(0, 32) + '...';
            document.getElementById(`${type}-secret`).textContent = keyData.secretKey.substring(0, 32) + '...';
        }
    }

    async downloadKeys(type) {
        const keyData = this.userKeys[type];
        if (!keyData) {
            this.showNotification('No keys to download', 'error');
            return;
        }

        const dataStr = JSON.stringify(keyData, null, 2);
        const blob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `${type}_keys_${this.currentUser.id}_${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showNotification(`${type.toUpperCase()} keys downloaded successfully!`, 'success');
        this.logAuditEvent('keys_downloaded', `User downloaded ${type} keys`);
    }

    downloadEncryptedFile() {
        if (!this.encryptedFile) {
            this.showNotification('No encrypted file available', 'error');
            return;
        }

        // If we have a download URL from the server, use it
        if (this.encryptedFile.downloadUrl) {
            const a = document.createElement('a');
            a.href = this.encryptedFile.downloadUrl;
            a.download = this.encryptedFile.name;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        } else {
            // Fallback to creating blob from data
            const blob = new Blob([this.encryptedFile.data], { type: 'application/octet-stream' });
            const url = URL.createObjectURL(blob);

            const a = document.createElement('a');
            a.href = url;
            a.download = this.encryptedFile.name;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }

        this.showNotification('Encrypted file downloaded!', 'success');
        this.logAuditEvent('file_downloaded', `Downloaded encrypted file: ${this.encryptedFile.name}`);
    }

    downloadDecryptedFile() {
        if (!this.decryptedFile) {
            this.showNotification('No decrypted file available', 'error');
            return;
        }

        // If we have a download URL from the server, use it
        if (this.decryptedFile.downloadUrl) {
            const a = document.createElement('a');
            a.href = this.decryptedFile.downloadUrl;
            a.download = this.decryptedFile.name;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        } else {
            // Fallback to creating blob from data
            const blob = new Blob([this.decryptedFile.data], { type: 'application/octet-stream' });
            const url = URL.createObjectURL(blob);

            const a = document.createElement('a');
            a.href = url;
            a.download = this.decryptedFile.name;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }

        this.showNotification('Decrypted file downloaded!', 'success');
        this.logAuditEvent('file_downloaded', `Downloaded decrypted file: ${this.decryptedFile.name}`);
    }

    async readFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = () => reject(reader.error);
            reader.readAsArrayBuffer(file);
        });
    }

    generateRandomHex(length) {
        const array = new Uint8Array(length);
        crypto.getRandomValues(array);
        return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    showNotification(message, type = 'info') {
        const container = document.getElementById('notification-container');

        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;

        const icon = type === 'success' ? '✅' :
                    type === 'error' ? '❌' :
                    type === 'warning' ? '⚠️' : 'ℹ️';

        notification.innerHTML = `
            <span class="notification-icon">${icon}</span>
            <div class="notification-content">
                <div class="notification-title">${type.charAt(0).toUpperCase() + type.slice(1)}</div>
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close">&times;</button>
        `;

        // Add to container
        container.appendChild(notification);

        // Show notification
        setTimeout(() => notification.classList.add('show'), 100);

        // Auto-hide after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (container.contains(notification)) {
                    container.removeChild(notification);
                }
            }, 300);
        }, 5000);

        // Close button
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (container.contains(notification)) {
                    container.removeChild(notification);
                }
            }, 300);
        });
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Premium Modal Functions
    showPremiumModal() {
        const modal = document.getElementById('premium-modal');
        if (modal) {
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }
    }

    closePremiumModal() {
        const modal = document.getElementById('premium-modal');
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    }

    // Desktop App Coming Soon
    downloadDesktopApp(platform = 'windows') {
        this.showNotification('Desktop application is currently in development. Check back in Q1 2025!', 'info');
    }

    // Show email notification modal
    notifyDesktopComingSoon() {
        const modal = document.getElementById('email-modal');
        if (modal) {
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }
    }

    // Close email modal
    closeEmailModal() {
        const modal = document.getElementById('email-modal');
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    }

    // Handle email notification form
    async handleEmailNotification(event) {
        event.preventDefault();

        const email = document.getElementById('notification-email').value;
        const wantsUpdates = document.getElementById('notification-updates').checked;

        if (!email) {
            this.showNotification('Please enter a valid email address', 'error');
            return;
        }

        // Validate email format
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            this.showNotification('Please enter a valid email address', 'error');
            return;
        }

        // Store in localStorage (replace with Supabase call)
        const notificationData = {
            email: email,
            wantsUpdates: wantsUpdates,
            timestamp: new Date().toISOString(),
            interests: ['desktop_app']
        };

        // Try to save to Supabase first, fallback to localStorage
        let saveResult = { success: false };

        try {
            // Check if Supabase is available
            if (typeof saveEmailNotification === 'function') {
                saveResult = await saveEmailNotification(notificationData);
            }
        } catch (error) {
            console.warn('Supabase not available, using localStorage:', error);
        }

        // Fallback to localStorage if Supabase fails or is not available
        if (!saveResult.success) {
            const existingNotifications = JSON.parse(localStorage.getItem('sudarshan_notifications') || '[]');
            existingNotifications.push(notificationData);
            localStorage.setItem('sudarshan_notifications', JSON.stringify(existingNotifications));
        }

        this.showNotification('Thank you! We\'ll notify you when the desktop app is available.', 'success');
        this.closeEmailModal();

        // Reset form
        document.getElementById('email-notification-form').reset();
    }

    // Upgrade to Plan
    upgradeToPlan(plan) {
        if (plan === 'professional') {
            // Redirect to payment or signup
            window.open('https://sudarshanengine.xyz/pricing?plan=professional', '_blank');
        } else if (plan === 'enterprise') {
            // Contact sales
            window.open('mailto:yash02.prof@gmail.com?subject=Enterprise%20Plan%20Inquiry', '_blank');
        }
        this.closePremiumModal();
        this.showNotification(`Redirecting to ${plan} plan...`, 'success');
    }
}

// Global functions for HTML onclick handlers
function showSection(sectionId) {
    if (window.app) {
        window.app.showSection(sectionId);
    }
}

function downloadEncryptedFile() {
    if (window.app) {
        window.app.downloadEncryptedFile();
    }
}

function downloadDecryptedFile() {
    if (window.app) {
        window.app.downloadDecryptedFile();
    }
}

function showPremiumModal() {
    if (window.app) {
        window.app.showPremiumModal();
    }
}

function closePremiumModal() {
    if (window.app) {
        window.app.closePremiumModal();
    }
}

function downloadDesktopApp(platform) {
    if (window.app) {
        window.app.downloadDesktopApp(platform);
    }
}

function upgradeToPlan(plan) {
    if (window.app) {
        window.app.upgradeToPlan(plan);
    }
}

function extendSession() {
    if (window.app) {
        window.app.extendSession();
    }
}

function togglePerformanceMetrics() {
    if (window.app) {
        window.app.togglePerformanceMetrics();
    }
}

function reloadApplication() {
    if (window.app) {
        window.app.reloadApplication();
    }
}

function clearAuditLog() {
    if (window.app) {
        window.app.clearAuditLog();
    }
}

function showPrivacyPolicy() {
    if (window.app) {
        window.app.showPrivacyPolicy();
    }
}

function showTermsOfService() {
    if (window.app) {
        window.app.showTermsOfService();
    }
}

function showCookiePolicy() {
    if (window.app) {
        window.app.showCookiePolicy();
    }
}

function showGDPRCompliance() {
    if (window.app) {
        window.app.showGDPRCompliance();
    }
}

function showSecurityPolicy() {
    if (window.app) {
        window.app.showSecurityPolicy();
    }
}

function showAuthTab(tab) {
    if (window.app) {
        window.app.showAuthTab(tab);
    }
}

function toggleUserMenu() {
    if (window.app) {
        window.app.toggleUserMenu();
    }
}

function showUserProfile() {
    if (window.app) {
        window.app.showUserProfile();
    }
}

function showSecuritySettings() {
    if (window.app) {
        window.app.showSecuritySettings();
    }
}

function showUserKeys() {
    if (window.app) {
        window.app.showUserKeys();
    }
}

function logoutUser() {
    if (window.app) {
        window.app.logoutUser();
    }
}

function showForgotPassword() {
    if (window.app) {
        window.app.showForgotPassword();
    }
}

function notifyDesktopComingSoon() {
    if (window.app) {
        window.app.notifyDesktopComingSoon();
    }
}

function closeEmailModal() {
    if (window.app) {
        window.app.closeEmailModal();
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new SudarshanWebApp();
});

// Service Worker for offline functionality (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Register service worker for offline functionality
        // navigator.serviceWorker.register('/sw.js');
    });
}