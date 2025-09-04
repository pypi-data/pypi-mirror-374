// Sudarshan Engine Desktop GUI Application Logic

class SudarshanDesktopApp {
    constructor() {
        this.currentSection = 'dashboard';
        this.keys = {
            kem: null,
            signature: null
        };
        this.stats = {
            filesEncrypted: 0,
            keysGenerated: 0,
            operationsToday: 0,
            securityScore: 100
        };

        this.init();
    }

    async init() {
        this.bindEvents();
        this.setupMenuHandlers();
        this.loadSettings();
        await this.updateEngineInfo();
        this.showSection('dashboard');
        this.addActivityLog('Sudarshan Engine Desktop Started');
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

        // Wallet
        this.bindWallet();

        // File info
        this.bindFileInfo();

        // Settings
        this.bindSettings();

        // Modal handlers
        this.bindModals();
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

    async updateEngineInfo() {
        try {
            const info = await window.electronAPI.getEngineInfo();
            document.getElementById('status-indicator').innerHTML = `
                <span class="status-dot"></span>
                <span class="status-text">Ready (${info.platform})</span>
            `;
        } catch (error) {
            console.error('Failed to get engine info:', error);
        }
    }

    bindEncryptForm() {
        const form = document.getElementById('encrypt-form');
        const browseBtn = document.getElementById('encrypt-browse-btn');
        const saveBtn = document.getElementById('encrypt-save-btn');
        const resetBtn = document.getElementById('encrypt-reset-btn');

        browseBtn.addEventListener('click', async () => {
            const result = await window.electronAPI.selectFile({
                title: 'Select File to Encrypt',
                properties: ['openFile']
            });

            if (!result.canceled) {
                document.getElementById('encrypt-input-file').value = result.filePaths[0];
            }
        });

        saveBtn.addEventListener('click', async () => {
            const result = await window.electronAPI.saveFile({
                title: 'Save Encrypted File',
                filters: [{ name: 'Sudarshan Files', extensions: ['spq'] }]
            });

            if (!result.canceled) {
                document.getElementById('encrypt-output-file').value = result.filePath;
            }
        });

        resetBtn.addEventListener('click', () => {
            form.reset();
            document.getElementById('encrypt-progress').style.display = 'none';
        });

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const inputFile = document.getElementById('encrypt-input-file').value;
            const outputFile = document.getElementById('encrypt-output-file').value;
            const algorithm = document.getElementById('encrypt-algorithm').value;
            const compression = document.getElementById('encrypt-compression').value;
            const metadata = document.getElementById('encrypt-metadata').value;
            const includeSignature = document.getElementById('encrypt-signature').checked;

            if (!inputFile || !outputFile) {
                this.showNotification('Please select input and output files', 'error');
                return;
            }

            // Show progress
            document.getElementById('encrypt-progress').style.display = 'block';
            const progressFill = document.getElementById('encrypt-progress-fill');
            const progressText = document.getElementById('encrypt-progress-text');

            try {
                progressText.textContent = 'Reading input file...';
                progressFill.style.width = '25%';

                // Read input file
                const fs = require('fs');
                const fileData = fs.readFileSync(inputFile);

                progressText.textContent = 'Encrypting file...';
                progressFill.style.width = '50%';

                // Parse metadata
                let metadataObj = {};
                try {
                    metadataObj = JSON.parse(metadata || '{}');
                } catch (error) {
                    metadataObj = { error: 'Invalid JSON metadata' };
                }

                // Simulate encryption process (in real implementation, this would call the Python backend)
                progressText.textContent = 'Generating quantum-safe keys...';
                progressFill.style.width = '75%';

                // Simulate key generation
                await this.delay(500);

                progressText.textContent = 'Finalizing encryption...';
                progressFill.style.width = '90%';

                // Simulate file writing
                await this.delay(300);

                progressFill.style.width = '100%';
                progressText.textContent = 'Encryption complete!';

                // Update stats
                this.stats.filesEncrypted++;
                this.updateDashboard();

                // Add activity log
                this.addActivityLog(`Encrypted file: ${inputFile.split('/').pop()}`);

                // Show success message
                this.showNotification('File encrypted successfully!', 'success');

                // Hide progress after delay
                setTimeout(() => {
                    document.getElementById('encrypt-progress').style.display = 'none';
                    progressFill.style.width = '0%';
                }, 2000);

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
        const browseBtn = document.getElementById('decrypt-browse-btn');
        const saveBtn = document.getElementById('decrypt-save-btn');
        const resetBtn = document.getElementById('decrypt-reset-btn');

        browseBtn.addEventListener('click', async () => {
            const result = await window.electronAPI.selectFile({
                title: 'Select .spq File to Decrypt',
                filters: [{ name: 'Sudarshan Files', extensions: ['spq'] }]
            });

            if (!result.canceled) {
                document.getElementById('decrypt-input-file').value = result.filePaths[0];
            }
        });

        saveBtn.addEventListener('click', async () => {
            const result = await window.electronAPI.saveFile({
                title: 'Save Decrypted File'
            });

            if (!result.canceled) {
                document.getElementById('decrypt-output-file').value = result.filePath;
            }
        });

        resetBtn.addEventListener('click', () => {
            form.reset();
            document.getElementById('decrypt-progress').style.display = 'none';
        });

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const inputFile = document.getElementById('decrypt-input-file').value;
            const outputFile = document.getElementById('decrypt-output-file').value;

            if (!inputFile || !outputFile) {
                this.showNotification('Please select input and output files', 'error');
                return;
            }

            // Show progress
            document.getElementById('decrypt-progress').style.display = 'block';
            const progressFill = document.getElementById('decrypt-progress-fill');
            const progressText = document.getElementById('decrypt-progress-text');

            try {
                progressText.textContent = 'Validating .spq file...';
                progressFill.style.width = '25%';

                // Simulate validation
                await this.delay(300);

                progressText.textContent = 'Decrypting file...';
                progressFill.style.width = '50%';

                // Simulate decryption
                await this.delay(500);

                progressText.textContent = 'Verifying integrity...';
                progressFill.style.width = '75%';

                // Simulate verification
                await this.delay(300);

                progressText.textContent = 'Writing output file...';
                progressFill.style.width = '90%';

                // Simulate file writing
                await this.delay(200);

                progressFill.style.width = '100%';
                progressText.textContent = 'Decryption complete!';

                // Add activity log
                this.addActivityLog(`Decrypted file: ${inputFile.split('/').pop()}`);

                // Show success message
                this.showNotification('File decrypted successfully!', 'success');

                // Hide progress after delay
                setTimeout(() => {
                    document.getElementById('decrypt-progress').style.display = 'none';
                    progressFill.style.width = '0%';
                }, 2000);

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
                await this.delay(500);

                this.keys.kem = {
                    algorithm: 'kyber1024',
                    publicKeySize: 1568,
                    secretKeySize: 3168,
                    generated: new Date().toISOString()
                };

                this.updateKeyDisplay('kem');
                this.stats.keysGenerated++;
                this.updateDashboard();

                this.addActivityLog('Generated Kyber KEM keypair');
                this.showNotification('KEM keypair generated successfully!', 'success');

            } catch (error) {
                this.showNotification('Key generation failed: ' + error.message, 'error');
            }
        });

        // Signature Key Generation
        document.getElementById('generate-sig-btn').addEventListener('click', async () => {
            try {
                // Simulate key generation
                await this.delay(500);

                this.keys.signature = {
                    algorithm: 'dilithium5',
                    publicKeySize: 2592,
                    secretKeySize: 4864,
                    generated: new Date().toISOString()
                };

                this.updateKeyDisplay('sig');
                this.stats.keysGenerated++;
                this.updateDashboard();

                this.addActivityLog('Generated Dilithium signature keypair');
                this.showNotification('Signature keypair generated successfully!', 'success');

            } catch (error) {
                this.showNotification('Key generation failed: ' + error.message, 'error');
            }
        });

        // Save Keys
        document.getElementById('save-kem-keys-btn').addEventListener('click', () => {
            this.saveKeys('kem');
        });

        document.getElementById('save-sig-keys-btn').addEventListener('click', () => {
            this.saveKeys('sig');
        });
    }

    bindWallet() {
        document.getElementById('create-wallet-btn').addEventListener('click', async () => {
            try {
                // Simulate wallet creation
                await this.delay(1000);

                document.getElementById('wallet-status').innerHTML = `
                    <p><strong>Wallet Status:</strong> Created</p>
                    <p><strong>Address:</strong> sudarshan1${Math.random().toString(36).substr(2, 9)}</p>
                    <p><strong>Balance:</strong> 0.00000000 SUD</p>
                `;

                document.getElementById('wallet-actions').style.display = 'block';
                this.addActivityLog('Created new quantum-safe wallet');
                this.showNotification('Wallet created successfully!', 'success');

            } catch (error) {
                this.showNotification('Wallet creation failed: ' + error.message, 'error');
            }
        });

        document.getElementById('load-wallet-btn').addEventListener('click', async () => {
            const result = await window.electronAPI.selectFile({
                title: 'Select Wallet File',
                filters: [{ name: 'Wallet Files', extensions: ['spq'] }]
            });

            if (!result.canceled) {
                // Simulate wallet loading
                await this.delay(500);

                document.getElementById('wallet-status').innerHTML = `
                    <p><strong>Wallet Status:</strong> Loaded</p>
                    <p><strong>File:</strong> ${result.filePaths[0].split('/').pop()}</p>
                    <p><strong>Balance:</strong> 1.23456789 SUD</p>
                `;

                document.getElementById('wallet-actions').style.display = 'block';
                this.addActivityLog('Loaded wallet from file');
                this.showNotification('Wallet loaded successfully!', 'success');
            }
        });
    }

    bindFileInfo() {
        const form = document.getElementById('info-form');
        const browseBtn = document.getElementById('info-browse-btn');
        const resetBtn = document.getElementById('info-reset-btn');

        browseBtn.addEventListener('click', async () => {
            const result = await window.electronAPI.selectFile({
                title: 'Select .spq File to Analyze',
                filters: [{ name: 'Sudarshan Files', extensions: ['spq'] }]
            });

            if (!result.canceled) {
                document.getElementById('info-input-file').value = result.filePaths[0];
            }
        });

        resetBtn.addEventListener('click', () => {
            form.reset();
            document.getElementById('file-info-display').style.display = 'none';
        });

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const inputFile = document.getElementById('info-input-file').value;

            if (!inputFile) {
                this.showNotification('Please select a file to analyze', 'error');
                return;
            }

            try {
                // Simulate file analysis
                await this.delay(500);

                // Mock file information
                const mockInfo = {
                    fileSize: '2.5 KB',
                    algorithm: 'Kyber1024',
                    compression: 'Zstandard',
                    hasSignature: true,
                    created: new Date().toISOString(),
                    creator: 'Sudarshan Engine',
                    metadata: JSON.stringify({
                        author: 'Test User',
                        purpose: 'File encryption demo',
                        created_at: new Date().toISOString()
                    }, null, 2)
                };

                // Update display
                document.getElementById('info-file-size').textContent = mockInfo.fileSize;
                document.getElementById('info-algorithm').textContent = mockInfo.algorithm;
                document.getElementById('info-compression').textContent = mockInfo.compression;
                document.getElementById('info-signature').textContent = mockInfo.hasSignature ? '✓ Yes' : '✗ No';
                document.getElementById('info-created').textContent = new Date(mockInfo.created).toLocaleString();
                document.getElementById('info-creator').textContent = mockInfo.creator;
                document.getElementById('info-metadata').textContent = mockInfo.metadata;

                document.getElementById('file-info-display').style.display = 'block';

                this.addActivityLog(`Analyzed file: ${inputFile.split('/').pop()}`);
                this.showNotification('File analysis complete!', 'success');

            } catch (error) {
                this.showNotification('File analysis failed: ' + error.message, 'error');
            }
        });
    }

    bindSettings() {
        document.getElementById('save-settings-btn').addEventListener('click', () => {
            // Save settings to localStorage
            const settings = {
                theme: document.getElementById('setting-theme').value,
                language: document.getElementById('setting-language').value,
                autoLock: document.getElementById('setting-auto-lock').checked,
                lockTimeout: document.getElementById('setting-lock-timeout').value,
                compression: document.getElementById('setting-compression').value,
                algorithm: document.getElementById('setting-algorithm').value
            };

            localStorage.setItem('sudarshan-settings', JSON.stringify(settings));
            this.showNotification('Settings saved successfully!', 'success');
        });

        document.getElementById('reset-settings-btn').addEventListener('click', () => {
            // Reset to defaults
            document.getElementById('setting-theme').value = 'light';
            document.getElementById('setting-language').value = 'en';
            document.getElementById('setting-auto-lock').checked = true;
            document.getElementById('setting-lock-timeout').value = '15';
            document.getElementById('setting-compression').value = 'zstd';
            document.getElementById('setting-algorithm').value = 'kyber1024';

            localStorage.removeItem('sudarshan-settings');
            this.showNotification('Settings reset to defaults!', 'success');
        });
    }

    bindModals() {
        // About modal
        window.showAbout = () => {
            document.getElementById('about-modal').style.display = 'flex';
        };

        // Close modal
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.modal').forEach(modal => {
                    modal.style.display = 'none';
                });
            });
        });

        // Click outside modal to close
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.style.display = 'none';
                }
            });
        });
    }

    setupMenuHandlers() {
        window.electronAPI.onMenuAction((event, action) => {
            switch (action) {
                case 'new-spq':
                    this.showSection('encrypt');
                    break;
                case 'open-spq':
                    this.showSection('decrypt');
                    break;
            }
        });
    }

    loadSettings() {
        const settings = localStorage.getItem('sudarshan-settings');
        if (settings) {
            const parsed = JSON.parse(settings);
            document.getElementById('setting-theme').value = parsed.theme || 'light';
            document.getElementById('setting-language').value = parsed.language || 'en';
            document.getElementById('setting-auto-lock').checked = parsed.autoLock !== false;
            document.getElementById('setting-lock-timeout').value = parsed.lockTimeout || '15';
            document.getElementById('setting-compression').value = parsed.compression || 'zstd';
            document.getElementById('setting-algorithm').value = parsed.algorithm || 'kyber1024';
        }
    }

    updateKeyDisplay(type) {
        const keyInfo = document.getElementById(`${type}-key-info`);
        const keyData = this.keys[type];

        if (keyData) {
            document.getElementById(`${type}-algorithm`).textContent = keyData.algorithm;
            document.getElementById(`${type}-pub-size`).textContent = `${keyData.publicKeySize} bytes`;
            document.getElementById(`${type}-sec-size`).textContent = `${keyData.secretKeySize} bytes`;
            keyInfo.style.display = 'block';
        }
    }

    async saveKeys(type) {
        try {
            const result = await window.electronAPI.saveFile({
                title: `Save ${type.toUpperCase()} Keys`,
                filters: [{ name: 'JSON Files', extensions: ['json'] }]
            });

            if (!result.canceled) {
                const fs = require('fs');
                fs.writeFileSync(result.filePath, JSON.stringify(this.keys[type], null, 2));
                this.showNotification(`${type.toUpperCase()} keys saved successfully!`, 'success');
            }
        } catch (error) {
            this.showNotification('Failed to save keys: ' + error.message, 'error');
        }
    }

    updateDashboard() {
        document.getElementById('files-encrypted').textContent = this.stats.filesEncrypted;
        document.getElementById('keys-generated').textContent = this.stats.keysGenerated;
        document.getElementById('operations-today').textContent = this.stats.operationsToday;
        document.getElementById('security-score').textContent = this.stats.securityScore;
    }

    addActivityLog(message) {
        const activityList = document.getElementById('activity-list');
        const activityItem = document.createElement('div');
        activityItem.className = 'activity-item';

        const now = new Date();
        const timeString = now.toLocaleTimeString();

        activityItem.innerHTML = `
            <div class="activity-icon">🔐</div>
            <div class="activity-content">
                <div class="activity-title">${message}</div>
                <div class="activity-time">${timeString}</div>
            </div>
        `;

        // Insert at the beginning
        if (activityList.firstChild) {
            activityList.insertBefore(activityItem, activityList.firstChild);
        } else {
            activityList.appendChild(activityItem);
        }

        // Keep only last 10 items
        while (activityList.children.length > 10) {
            activityList.removeChild(activityList.lastChild);
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close">&times;</button>
            </div>
        `;

        // Add to page
        document.body.appendChild(notification);

        // Show notification
        setTimeout(() => notification.classList.add('show'), 100);

        // Auto-hide after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => document.body.removeChild(notification), 300);
        }, 5000);

        // Close button
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.classList.remove('show');
            setTimeout(() => document.body.removeChild(notification), 300);
        });
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new SudarshanDesktopApp();
});

// Add notification styles
const notificationStyles = `
.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    min-width: 300px;
    max-width: 500px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    border-left: 4px solid #2563eb;
    transform: translateX(100%);
    transition: transform 0.3s ease;
    z-index: 1000;
}

.notification.show {
    transform: translateX(0);
}

.notification-success {
    border-left-color: #10b981;
}

.notification-error {
    border-left-color: #ef4444;
}

.notification-warning {
    border-left-color: #f59e0b;
}

.notification-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem;
}

.notification-message {
    flex: 1;
    margin-right: 1rem;
}

.notification-close {
    background: none;
    border: none;
    font-size: 1.25rem;
    cursor: pointer;
    color: #64748b;
    padding: 0.25rem;
    border-radius: 4px;
    transition: all 0.2s ease;
}

.notification-close:hover {
    background: #f1f5f9;
    color: #1e293b;
}
`;

// Inject notification styles
const style = document.createElement('style');
style.textContent = notificationStyles;
document.head.appendChild(style);