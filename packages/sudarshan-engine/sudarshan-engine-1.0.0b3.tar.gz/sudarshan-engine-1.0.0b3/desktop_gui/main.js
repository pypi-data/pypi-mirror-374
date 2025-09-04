const { app, BrowserWindow, ipcMain, dialog, Menu } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

// Keep a global reference of the window object
let mainWindow;

// Python process reference
let pythonProcess = null;

function createWindow() {
    // Create the browser window
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        minWidth: 800,
        minHeight: 600,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            enableRemoteModule: false,
            preload: path.join(__dirname, 'preload.js')
        },
        icon: path.join(__dirname, 'assets/icon.png'),
        title: 'Sudarshan Engine - Quantum-Safe Desktop',
        show: false
    });

    // Load the app
    mainWindow.loadFile('src/index.html');

    // Show window when ready to prevent visual flash
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
    });

    // Emitted when the window is closed
    mainWindow.on('closed', () => {
        mainWindow = null;
        if (pythonProcess) {
            pythonProcess.kill();
            pythonProcess = null;
        }
    });

    // Open DevTools in development
    if (process.env.NODE_ENV === 'development') {
        mainWindow.webContents.openDevTools();
    }
}

// Start Python backend
function startPythonBackend() {
    const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
    const sudarshanPath = path.join(__dirname, '..', 'sudarshan.py');

    pythonProcess = spawn(pythonPath, [sudarshanPath, '--serve'], {
        cwd: path.join(__dirname, '..'),
        stdio: ['pipe', 'pipe', 'pipe']
    });

    pythonProcess.stdout.on('data', (data) => {
        console.log(`Python: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Python Error: ${data}`);
    });

    pythonProcess.on('close', (code) => {
        console.log(`Python process exited with code ${code}`);
        pythonProcess = null;
    });
}

// IPC handlers for communication with renderer
ipcMain.handle('get-engine-info', async () => {
    return {
        name: 'Sudarshan Engine Desktop',
        version: '1.0.0',
        platform: process.platform,
        arch: process.arch
    };
});

ipcMain.handle('select-file', async (event, options) => {
    const result = await dialog.showOpenDialog(mainWindow, {
        title: options.title || 'Select File',
        properties: options.properties || ['openFile'],
        filters: options.filters || []
    });
    return result;
});

ipcMain.handle('save-file', async (event, options) => {
    const result = await dialog.showSaveDialog(mainWindow, {
        title: options.title || 'Save File',
        filters: options.filters || []
    });
    return result;
});

ipcMain.handle('execute-sudarshan', async (event, command, args) => {
    return new Promise((resolve, reject) => {
        const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
        const sudarshanPath = path.join(__dirname, '..', 'sudarshan.py');

        const process = spawn(pythonPath, [sudarshanPath, command, ...args], {
            cwd: path.join(__dirname, '..')
        });

        let stdout = '';
        let stderr = '';

        process.stdout.on('data', (data) => {
            stdout += data.toString();
        });

        process.stderr.on('data', (data) => {
            stderr += data.toString();
        });

        process.on('close', (code) => {
            if (code === 0) {
                resolve({ success: true, output: stdout });
            } else {
                resolve({ success: false, error: stderr, output: stdout });
            }
        });

        process.on('error', (error) => {
            reject(error);
        });
    });
});

// Application menu
const template = [
    {
        label: 'File',
        submenu: [
            {
                label: 'New .spq File',
                accelerator: 'CmdOrCtrl+N',
                click: () => {
                    mainWindow.webContents.send('menu-action', 'new-spq');
                }
            },
            {
                label: 'Open .spq File',
                accelerator: 'CmdOrCtrl+O',
                click: () => {
                    mainWindow.webContents.send('menu-action', 'open-spq');
                }
            },
            { type: 'separator' },
            {
                label: 'Exit',
                accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
                click: () => {
                    app.quit();
                }
            }
        ]
    },
    {
        label: 'View',
        submenu: [
            { role: 'reload' },
            { role: 'forceReload' },
            { role: 'toggleDevTools' },
            { type: 'separator' },
            { role: 'resetZoom' },
            { role: 'zoomIn' },
            { role: 'zoomOut' },
            { type: 'separator' },
            { role: 'togglefullscreen' }
        ]
    },
    {
        label: 'Help',
        submenu: [
            {
                label: 'About Sudarshan Engine',
                click: () => {
                    dialog.showMessageBox(mainWindow, {
                        type: 'info',
                        title: 'About Sudarshan Engine',
                        message: 'Sudarshan Engine Desktop',
                        detail: 'Quantum-safe cybersecurity engine for protecting digital assets against current and future threats.'
                    });
                }
            }
        ]
    }
];

// Set application menu
const menu = Menu.buildFromTemplate(template);
Menu.setApplicationMenu(menu);

// App event handlers
app.whenReady().then(() => {
    createWindow();
    startPythonBackend();
});

app.on('window-all-closed', () => {
    // On macOS, keep app running even when all windows are closed
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    // On macOS, re-create window when dock icon is clicked
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

// Handle app security
app.on('web-contents-created', (event, contents) => {
    contents.on('new-window', (event, navigationUrl) => {
        // Prevent new window creation
        event.preventDefault();
    });

    contents.on('will-navigate', (event, navigationUrl) => {
        // Prevent navigation to external URLs
        const parsedUrl = new URL(navigationUrl);
        if (parsedUrl.origin !== 'file://') {
            event.preventDefault();
        }
    });
});