// ===== Device Management JavaScript =====

// Global variables
let currentUser = null;
let allDevices = [];
let currentFilter = 'all';
let currentDeviceData = null;

// Initialize page when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Device Management: Initializing...');
    
    // Check authentication
    currentUser = await fallDetection.checkAuthState();
    if (!currentUser) {
        console.log('No user logged in, redirecting to login');
        window.location.href = '/login';
        return;
    }

    console.log('User authenticated:', currentUser.email);
    
    // Setup event listeners
    setupEventListeners();
    
    // Load devices
    await loadDevices();
    
    // Setup auto-refresh every 30 seconds
    setInterval(loadDevices, 30000);
});

// Setup all event listeners
function setupEventListeners() {
    // Logout button
    document.getElementById('logoutBtn').addEventListener('click', async (e) => {
        e.preventDefault();
        await fallDetection.signOut();
        window.location.href = '/login';
    });

    // Create device button
    const createBtn = document.getElementById('createDeviceBtn');
    if (createBtn) {
        createBtn.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('Create device button clicked');
            openCreateModal();
        });
    } else {
        console.error('Create device button not found!');
    }

    // Create device form
    document.getElementById('createDeviceForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await createDevice();
    });

    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            setFilter(e.target.dataset.filter);
        });
    });

    // Close modal on background click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    });
}

// Load devices from API
async function loadDevices() {
    try {
        console.log('Loading devices for user:', currentUser.uid);
        
        const token = await fallDetection.getUserToken();
        const response = await fetch(`/api/devices?user_id=${currentUser.uid}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error(`Failed to load devices: ${response.status}`);
        }

        const data = await response.json();
        console.log('Devices loaded:', data);

        allDevices = data.devices || [];
        
        // Update stats
        updateStats();
        
        // Render devices
        renderDevices();
        
    } catch (error) {
        console.error('Error loading devices:', error);
        showError('Failed to load devices. Please refresh the page.');
    }
}

// Update statistics cards
function updateStats() {
    const total = allDevices.length;
    const online = allDevices.filter(d => d.status === 'online').length;
    const paired = allDevices.filter(d => d.isPaired).length;
    const unpaired = allDevices.filter(d => !d.isPaired).length;

    document.getElementById('totalDevices').textContent = total;
    document.getElementById('onlineDevices').textContent = online;
    document.getElementById('pairedDevices').textContent = paired;
    document.getElementById('unpairedDevices').textContent = unpaired;
}

// Render devices grid
function renderDevices() {
    const grid = document.getElementById('devicesGrid');
    const loading = document.getElementById('loadingDevices');
    const empty = document.getElementById('emptyState');

    // Hide loading
    loading.style.display = 'none';

    // Filter devices
    let filteredDevices = allDevices;
    if (currentFilter === 'online') {
        filteredDevices = allDevices.filter(d => d.status === 'online');
    } else if (currentFilter === 'paired') {
        filteredDevices = allDevices.filter(d => d.isPaired);
    } else if (currentFilter === 'unpaired') {
        filteredDevices = allDevices.filter(d => !d.isPaired);
    }

    // Show empty state if no devices
    if (filteredDevices.length === 0) {
        grid.style.display = 'none';
        empty.style.display = 'block';
        return;
    }

    // Show grid and render devices
    empty.style.display = 'none';
    grid.style.display = 'grid';
    grid.innerHTML = filteredDevices.map(device => createDeviceCard(device)).join('');

    // Add event listeners to action buttons
    addDeviceActionListeners();
}

// Create device card HTML
function createDeviceCard(device) {
    const isOnline = device.status === 'online';
    const isPaired = device.isPaired;
    const batteryLevel = device.batteryLevel || 0;
    const batteryClass = batteryLevel > 60 ? 'high' : batteryLevel > 30 ? 'medium' : 'low';
    
    // Calculate time since last heartbeat
    let lastSeen = 'Never';
    if (device.lastHeartbeat) {
        const lastHeartbeatDate = new Date(device.lastHeartbeat);
        const now = new Date();
        const diffMinutes = Math.floor((now - lastHeartbeatDate) / (1000 * 60));
        if (diffMinutes < 1) {
            lastSeen = 'Just now';
        } else if (diffMinutes < 60) {
            lastSeen = `${diffMinutes}m ago`;
        } else if (diffMinutes < 1440) {
            lastSeen = `${Math.floor(diffMinutes / 60)}h ago`;
        } else {
            lastSeen = `${Math.floor(diffMinutes / 1440)}d ago`;
        }
    }

    // Format created date
    const createdDate = device.createdAt ? new Date(device.createdAt).toLocaleString() : 'Unknown';

    return `
        <div class="device-card" data-device-id="${device.deviceId}">
            <div class="device-header">
                <div class="device-title">
                    <h3>
                        <i class="fas fa-microchip"></i>
                        ${device.name || 'Unnamed Device'}
                    </h3>
                    <div class="device-id">${device.deviceId}</div>
                </div>
                <span class="status-badge ${isOnline ? 'online' : 'offline'}">
                    ${isOnline ? '● Online' : '○ Offline'}
                </span>
            </div>

            <div class="device-info">
                <div class="info-row">
                    <span class="info-label">
                        <i class="fas fa-link"></i> Status
                    </span>
                    <span class="status-badge ${isPaired ? 'paired' : 'unpaired'}">
                        ${isPaired ? 'Paired' : 'Unpaired'}
                    </span>
                </div>
                
                <div class="info-row">
                    <span class="info-label">
                        <i class="fas fa-battery-three-quarters"></i> Battery
                    </span>
                    <div class="battery-indicator">
                        <div class="battery-bar">
                            <div class="battery-fill ${batteryClass}" style="width: ${batteryLevel}%"></div>
                        </div>
                        <span class="info-value">${batteryLevel}%</span>
                    </div>
                </div>

                <div class="info-row">
                    <span class="info-label">
                        <i class="fas fa-clock"></i> Last Seen
                    </span>
                    <span class="info-value">${lastSeen}</span>
                </div>

                ${device.location ? `
                <div class="info-row">
                    <span class="info-label">
                        <i class="fas fa-map-marker-alt"></i> Location
                    </span>
                    <span class="info-value">${device.location}</span>
                </div>
                ` : ''}
            </div>

            ${!isPaired && device.pairingCode ? `
            <div class="pairing-code-box">
                <div style="font-size: 0.9rem; color: #718096;">Pairing Code:</div>
                <div class="code">${device.pairingCode}</div>
                <div class="expiry">
                    <i class="fas fa-clock"></i> 
                    Expires in ${calculateExpiry(device.pairingCodeExpiry)}
                </div>
            </div>
            ` : ''}

            <div class="device-actions">
                <button class="btn-icon primary" onclick="viewDeviceDetails('${device.deviceId}')">
                    <i class="fas fa-info-circle"></i> Details
                </button>
                ${!isPaired ? `
                <button class="btn-icon secondary" onclick="regeneratePairingCode('${device.deviceId}')">
                    <i class="fas fa-sync"></i> New Code
                </button>
                ` : ''}
                <button class="btn-icon danger" onclick="deleteDevice('${device.deviceId}')">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `;
}

// Calculate expiry time remaining
function calculateExpiry(expiryTimestamp) {
    if (!expiryTimestamp) return 'Unknown';
    
    const expiry = new Date(expiryTimestamp);
    const now = new Date();
    const diffMinutes = Math.floor((expiry - now) / (1000 * 60));
    
    if (diffMinutes < 0) return 'Expired';
    if (diffMinutes < 60) return `${diffMinutes} minutes`;
    
    const hours = Math.floor(diffMinutes / 60);
    const minutes = diffMinutes % 60;
    return `${hours}h ${minutes}m`;
}

// Add event listeners to device action buttons
function addDeviceActionListeners() {
    // Already using onclick attributes in HTML
    // This is here for future enhancements
}

// Set filter
function setFilter(filter) {
    currentFilter = filter;
    
    // Update button states
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.filter === filter);
    });
    
    // Re-render devices
    renderDevices();
}

// Open create device modal
function openCreateModal() {
    console.log('Opening create device modal...');
    const modal = document.getElementById('createDeviceModal');
    if (!modal) {
        console.error('Create device modal not found!');
        alert('Error: Modal not found. Please refresh the page.');
        return;
    }
    console.log('Modal found, adding active class');
    modal.classList.add('active');
    
    const nameInput = document.getElementById('deviceName');
    if (nameInput) {
        nameInput.focus();
    }
    console.log('Modal should be visible now');
}

// Close create device modal
function closeCreateModal() {
    const modal = document.getElementById('createDeviceModal');
    modal.classList.remove('active');
    document.getElementById('createDeviceForm').reset();
    document.getElementById('createError').style.display = 'none';
}

// Create new device
async function createDevice() {
    const submitBtn = document.getElementById('createSubmitBtn');
    const errorDiv = document.getElementById('createError');
    
    try {
        // Get form data
        const name = document.getElementById('deviceName').value.trim();
        const location = document.getElementById('deviceLocation').value.trim();
        
        if (!name) {
            throw new Error('Device name is required');
        }

        // Disable button and show loading
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';
        errorDiv.style.display = 'none';

        // Get auth token
        const token = await fallDetection.getUserToken();

        // Create device
        const response = await fetch('/api/devices/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                userId: currentUser.uid,
                name: name,
                location: location || ''
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to create device');
        }

        const data = await response.json();
        console.log('Device created:', data);
        console.log('Device object:', data.device);
        console.log('Pairing code:', data.device.pairingCode);

        // Store device data
        currentDeviceData = data.device;

        // Close create modal
        closeCreateModal();

        // Show pairing code modal with proper data
        showPairingCodeModal(data.device);

        // Reload devices
        await loadDevices();

    } catch (error) {
        console.error('Error creating device:', error);
        errorDiv.textContent = error.message;
        errorDiv.style.display = 'block';
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-plus"></i> Create Device';
    }
}

// Show pairing code modal
function showPairingCodeModal(device) {
    console.log('showPairingCodeModal called with:', device);
    
    const modal = document.getElementById('pairingModal');
    const codeDisplay = document.getElementById('pairingCodeDisplay');
    const deviceIdSpan = document.getElementById('newDeviceId');
    const deviceTimeSpan = document.getElementById('newDeviceTime');

    if (!modal) {
        console.error('Pairing modal not found!');
        alert('Error: Modal not found');
        return;
    }

    if (!codeDisplay) {
        console.error('Code display element not found!');
        return;
    }

    // Set the pairing code
    const pairingCode = device.pairingCode || device.pairing_code || 'ERROR';
    console.log('Setting pairing code:', pairingCode);
    codeDisplay.textContent = pairingCode;
    
    // Set device ID
    if (deviceIdSpan) {
        deviceIdSpan.textContent = device.deviceId || device.device_id || 'Unknown';
    }
    
    // Set timestamp
    if (deviceTimeSpan) {
        deviceTimeSpan.textContent = new Date().toLocaleString();
    }

    // Show modal
    modal.classList.add('active');
    console.log('Modal should be visible now with code:', pairingCode);
}

// Close pairing code modal
function closePairingModal() {
    const modal = document.getElementById('pairingModal');
    modal.classList.remove('active');
    currentDeviceData = null;
}

// Copy pairing code to clipboard
async function copyPairingCode() {
    const codeElement = document.getElementById('pairingCodeDisplay');
    const code = codeElement.textContent;
    
    console.log('Copying code:', code);
    
    if (!code || code === '------' || code === 'ERROR') {
        alert('No valid pairing code to copy');
        return;
    }
    
    try {
        await navigator.clipboard.writeText(code);
        
        // Show success feedback
        const btn = event.target.closest('.btn-copy');
        if (btn) {
            const originalText = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
            btn.style.background = '#10b981';
            
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.style.background = '#667eea';
            }, 2000);
        }
        
        console.log('Code copied successfully');
        
    } catch (error) {
        console.error('Failed to copy:', error);
        // Fallback: select and copy manually
        alert('Please copy manually: ' + code);
    }
}

// View device details
async function viewDeviceDetails(deviceId) {
    const device = allDevices.find(d => d.deviceId === deviceId);
    if (!device) return;

    const modal = document.getElementById('deviceDetailsModal');
    const content = document.getElementById('deviceDetailsContent');

    content.innerHTML = `
        <div style="padding: 1.5rem;">
            <h3 style="margin: 0 0 1rem 0; color: #1a202c;">
                <i class="fas fa-microchip"></i> ${device.name || 'Unnamed Device'}
            </h3>
            
            <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                <p style="margin: 0.5rem 0;"><strong>Device ID:</strong> ${device.deviceId}</p>
                <p style="margin: 0.5rem 0;"><strong>Status:</strong> ${device.status}</p>
                <p style="margin: 0.5rem 0;"><strong>Paired:</strong> ${device.isPaired ? 'Yes' : 'No'}</p>
                <p style="margin: 0.5rem 0;"><strong>Battery:</strong> ${device.batteryLevel}%</p>
                ${device.location ? `<p style="margin: 0.5rem 0;"><strong>Location:</strong> ${device.location}</p>` : ''}
                <p style="margin: 0.5rem 0;"><strong>Created:</strong> ${new Date(device.createdAt).toLocaleString()}</p>
                ${device.lastHeartbeat ? `<p style="margin: 0.5rem 0;"><strong>Last Heartbeat:</strong> ${new Date(device.lastHeartbeat).toLocaleString()}</p>` : ''}
            </div>

            ${!device.isPaired && device.pairingCode ? `
            <div class="alert alert-info">
                <i class="fas fa-key"></i>
                <div>
                    <strong>Pairing Code:</strong> ${device.pairingCode}<br>
                    <small>Expires: ${new Date(device.pairingCodeExpiry).toLocaleString()}</small>
                </div>
            </div>
            ` : ''}
        </div>
        <div class="modal-actions">
            <button class="btn btn-primary" onclick="closeDetailsModal()">Close</button>
        </div>
    `;

    modal.classList.add('active');
}

// Close device details modal
function closeDetailsModal() {
    const modal = document.getElementById('deviceDetailsModal');
    modal.classList.remove('active');
}

// Regenerate pairing code
async function regeneratePairingCode(deviceId) {
    if (!confirm('Generate a new pairing code? The old code will no longer work.')) {
        return;
    }

    try {
        const token = await fallDetection.getUserToken();
        
        // Call API to regenerate code (you'll need to implement this endpoint)
        const response = await fetch(`/api/devices/${deviceId}/regenerate-code`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to regenerate code');
        }

        const data = await response.json();
        
        // Show new code
        alert(`New pairing code: ${data.pairingCode}\n\nThis code will expire in 15 minutes.`);
        
        // Reload devices
        await loadDevices();

    } catch (error) {
        console.error('Error regenerating code:', error);
        alert('Failed to regenerate code. Please try again.');
    }
}

// Delete device
async function deleteDevice(deviceId) {
    const device = allDevices.find(d => d.deviceId === deviceId);
    const deviceName = device ? device.name : deviceId;

    if (!confirm(`Are you sure you want to delete "${deviceName}"?\n\nThis action cannot be undone.`)) {
        return;
    }

    try {
        const token = await fallDetection.getUserToken();
        
        const response = await fetch(`/api/devices/${deviceId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to delete device');
        }

        // Show success message
        showSuccess('Device deleted successfully');
        
        // Reload devices
        await loadDevices();

    } catch (error) {
        console.error('Error deleting device:', error);
        showError('Failed to delete device. Please try again.');
    }
}

// Show error message
function showError(message) {
    // You can implement a toast notification here
    console.error(message);
    alert(message);
}

// Show success message
function showSuccess(message) {
    // You can implement a toast notification here
    console.log(message);
}

// Make functions globally available
window.closeCreateModal = closeCreateModal;
window.closePairingModal = closePairingModal;
window.closeDetailsModal = closeDetailsModal;
window.copyPairingCode = copyPairingCode;
window.viewDeviceDetails = viewDeviceDetails;
window.regeneratePairingCode = regeneratePairingCode;
window.deleteDevice = deleteDevice;
