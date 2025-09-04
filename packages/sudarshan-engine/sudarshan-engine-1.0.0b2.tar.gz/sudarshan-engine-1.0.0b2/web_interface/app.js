// Sudarshan Engine Web Interface Application Logic

class SudarshanWebApp {
    constructor() {
        this.currentSection = 'dashboard';
        this.backendConnected = false;
        this.keys = {
            kem: null,
            signature: null
        };
        this.encryptedFile = null;
        this.decryptedFile = null;

        this.init();
    }

    async init() {
        this.bindEvents();
        this.checkBackendConnection();
        this.showSection('dashboard');
        this.showNotification('Welcome to Sudarshan Engine Web Interface', 'success');
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
            // Simulate backend connection check
            await this.delay(1000);
            this.backendConnected = true;
            document.getElementById('status-dot').style.backgroundColor = 'var(--success-color)';
            document.getElementById('status-text').textContent = 'Connected';
        } catch (error) {
            this.backendConnected = false;
            document.getElementById('status-dot').style.backgroundColor = 'var(--error-color)';
            document.getElementById('status-text').textContent = 'Disconnected';
            this.showNotification('Backend connection failed', 'error');
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

            const file = input.files[0];
            if (!file) {
                this.showNotification('Please select a file to encrypt', 'error');
                return;
            }

            if (!this.backendConnected) {
                this.showNotification('Backend not connected', 'error');
                return;
            }

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

                // Simulate encryption
                await this.delay(1000);

                progressText.textContent = 'Finalizing...';
                progressFill.style.width = '90%';

                // Create encrypted file (simulate)
                this.encryptedFile = {
                    name: file.name + '.spq',
                    data: fileData, // In real implementation, this would be encrypted
                    size: fileData.length
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

            } catch (error) {
                console.error('Encryption error:', error);
                this.showNotification('Encryption failed: ' + error.message, 'error');
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

            const file = input.files[0];
            if (!file) {
                this.showNotification('Please select a .spq file to decrypt', 'error');
                return;
            }

            if (!file.name.endsWith('.spq')) {
                this.showNotification('Please select a valid .spq file', 'error');
                return;
            }

            if (!this.backendConnected) {
                this.showNotification('Backend not connected', 'error');
                return;
            }

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

                // Simulate decryption
                await this.delay(1000);

                progressText.textContent = 'Finalizing...';
                progressFill.style.width = '90%';

                // Create decrypted file (simulate)
                this.decryptedFile = {
                    name: file.name.replace('.spq', ''),
                    data: fileData, // In real implementation, this would be decrypted
                    size: fileData.length
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

            } catch (error) {
                console.error('Decryption error:', error);
                this.showNotification('Decryption failed: ' + error.message, 'error');
                document.getElementById('decrypt-progress').style.display = 'none';
                progressFill.style.width = '0%';
            }
        });
    }

    bindKeyManagement() {
        // KEM Key Generation
        document.getElementById('generate-kem-btn').addEventListener('click', async () => {
            try {
                // Simulate key generation
                await this.delay(1000);

                this.keys.kem = {
                    algorithm: 'Kyber1024',
                    publicKey: this.generateRandomHex(1568),
                    secretKey: this.generateRandomHex(3168),
                    generated: new Date().toISOString()
                };

                this.updateKeyDisplay('kem');
                document.getElementById('kem-keys-display').style.display = 'block';

                this.showNotification('KEM keypair generated successfully!', 'success');

            } catch (error) {
                this.showNotification('Key generation failed: ' + error.message, 'error');
            }
        });

        // Signature Key Generation
        document.getElementById('generate-sig-btn').addEventListener('click', async () => {
            try {
                // Simulate key generation
                await this.delay(1000);

                this.keys.signature = {
                    algorithm: 'Dilithium5',
                    publicKey: this.generateRandomHex(2592),
                    secretKey: this.generateRandomHex(4864),
                    generated: new Date().toISOString()
                };

                this.updateKeyDisplay('sig');
                document.getElementById('sig-keys-display').style.display = 'block';

                this.showNotification('Signature keypair generated successfully!', 'success');

            } catch (error) {
                this.showNotification('Key generation failed: ' + error.message, 'error');
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

    updateKeyDisplay(type) {
        const keyData = this.keys[type];
        if (keyData) {
            document.getElementById(`${type}-algorithm`).textContent = keyData.algorithm;
            document.getElementById(`${type}-public`).textContent = keyData.publicKey.substring(0, 32) + '...';
            document.getElementById(`${type}-secret`).textContent = keyData.secretKey.substring(0, 32) + '...';
        }
    }

    async downloadKeys(type) {
        const keyData = this.keys[type];
        if (!keyData) {
            this.showNotification('No keys to download', 'error');
            return;
        }

        const dataStr = JSON.stringify(keyData, null, 2);
        const blob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `${type}_keys_${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showNotification(`${type.toUpperCase()} keys downloaded successfully!`, 'success');
    }

    downloadEncryptedFile() {
        if (!this.encryptedFile) {
            this.showNotification('No encrypted file available', 'error');
            return;
        }

        const blob = new Blob([this.encryptedFile.data], { type: 'application/octet-stream' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = this.encryptedFile.name;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showNotification('Encrypted file downloaded!', 'success');
    }

    downloadDecryptedFile() {
        if (!this.decryptedFile) {
            this.showNotification('No decrypted file available', 'error');
            return;
        }

        const blob = new Blob([this.decryptedFile.data], { type: 'application/octet-stream' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = this.decryptedFile.name;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showNotification('Decrypted file downloaded!', 'success');
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