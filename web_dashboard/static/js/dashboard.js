/**
 * Dashboard JavaScript
 * Handles data fetching, chart rendering, and real-time updates
 */

// Global state
let currentUser = null;
let devicesData = [];
let charts = {};
let socket = null;

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', async () => {
    console.log('📊 Dashboard initializing...');
    
    // Check authentication
    currentUser = await fallDetection.checkAuthState();
    
    if (!currentUser) {
        console.log('❌ No authenticated user, redirecting to login...');
        window.location.href = '/login';
        return;
    }
    
    console.log('✓ User authenticated:', currentUser.email);
    
    // Display user name
    const userName = document.getElementById('userName');
    if (userName) {
        userName.textContent = currentUser.displayName || currentUser.email.split('@')[0];
    }
    
    // Setup logout button
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            await fallDetection.signOut();
            window.location.href = '/login';
        });
    }
    
    // Initialize WebSocket connection
    initializeWebSocket();
    
    // Load dashboard data
    await loadDashboardData();
    
    // Setup auto-refresh every 30 seconds as fallback
    setInterval(loadDashboardData, 30000);
    
    console.log('✓ Dashboard initialized successfully');
});

/**
 * Initialize WebSocket connection
 */
function initializeWebSocket() {
    try {
        console.log('🔌 Connecting to WebSocket...');
        
        // Connect to Socket.IO server
        socket = io({
            transports: ['websocket', 'polling']
        });
        
        // Connection events
        socket.on('connect', () => {
            console.log('✓ WebSocket connected');
            
            // Join dashboard room for updates
            socket.emit('join_dashboard', {
                userId: currentUser.uid
            });
        });
        
        socket.on('disconnect', () => {
            console.log('⚠️  WebSocket disconnected');
        });
        
        socket.on('connection_response', (data) => {
            console.log('✓ WebSocket handshake:', data.message);
        });
        
        socket.on('joined_dashboard', (data) => {
            console.log('✓ Joined dashboard room:', data.message);
        });
        
        // Real-time updates
        socket.on('device_status_update', (data) => {
            console.log('📡 Device status update:', data);
            handleDeviceStatusUpdate(data);
        });
        
        socket.on('fall_detected', (data) => {
            console.log('🚨 FALL DETECTED:', data);
            handleFallAlert(data);
        });
        
        socket.on('sensor_data', (data) => {
            console.log('📊 Sensor data:', data);
            handleSensorData(data);
        });
        
    } catch (error) {
        console.error('Error initializing WebSocket:', error);
    }
}

/**
 * Handle real-time device status update
 */
function handleDeviceStatusUpdate(data) {
    // Update device in local data
    const deviceIndex = devicesData.findIndex(d => d.deviceId === data.deviceId);
    
    if (deviceIndex !== -1) {
        devicesData[deviceIndex].status = data.status;
        devicesData[deviceIndex].batteryLevel = data.batteryLevel;
        devicesData[deviceIndex].lastSeen = data.lastSeen;
        
        // Update stats
        updateStats();
        
        // Update charts
        renderCharts();
        
        // Update table
        renderDevicesTable();
        
        // Show notification
        showNotification('info', `Device ${devicesData[deviceIndex].name || data.deviceId} updated`, 
                        `Status: ${data.status}, Battery: ${data.batteryLevel}%`);
    }
}

/**
 * Handle fall alert
 */
function handleFallAlert(data) {
    // Show critical alert
    showNotification('danger', '🚨 FALL DETECTED!', 
                    `Device ${data.deviceId} detected a fall at ${new Date(data.timestamp).toLocaleTimeString()}`);
    
    // Play alert sound (optional)
    // playAlertSound();
    
    // Reload data to update fall count
    loadDashboardData();
}

/**
 * Handle sensor data
 */
function handleSensorData(data) {
    // Update real-time charts if on monitoring page
    // This is handled in monitoring.html
    console.log('Sensor data received:', data.deviceId);
}

/**
 * Show notification
 */
function showNotification(type, title, message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <strong>${title}</strong>
            <p>${message}</p>
        </div>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

/**
 * Load all dashboard data
 */
async function loadDashboardData() {
    try {
        console.log('🔄 Loading dashboard data...');
        
        // Fetch devices
        await fetchDevices();
        
        // Update stats
        updateStats();
        
        // Render charts
        renderCharts();
        
        // Render devices table
        renderDevicesTable();
        
        // Render recent activity
        renderRecentActivity();
        
        console.log('✓ Dashboard data loaded');
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

/**
 * Fetch devices from API
 */
async function fetchDevices() {
    try {
        const token = await fallDetection.getUserToken();
        const response = await fetch(`/api/devices?user_id=${currentUser.uid}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            devicesData = data.devices || [];
            console.log(`✓ Fetched ${devicesData.length} devices`);
        } else {
            console.error('Failed to fetch devices:', data.error);
            devicesData = [];
        }
    } catch (error) {
        console.error('Error fetching devices:', error);
        devicesData = [];
    }
}

/**
 * Update statistics cards
 */
function updateStats() {
    const totalDevices = devicesData.length;
    const onlineDevices = devicesData.filter(d => d.status === 'online').length;
    const totalAlerts = 0; // TODO: Fetch from fall_events collection
    const avgBattery = totalDevices > 0 
        ? Math.round(devicesData.reduce((sum, d) => sum + (d.batteryLevel || 0), 0) / totalDevices)
        : 0;
    
    document.getElementById('totalDevices').textContent = totalDevices;
    document.getElementById('onlineDevices').textContent = onlineDevices;
    document.getElementById('totalAlerts').textContent = totalAlerts;
    document.getElementById('avgBattery').textContent = avgBattery > 0 ? `${avgBattery}%` : '--';
}

/**
 * Render all charts
 */
function renderCharts() {
    renderDeviceStatusChart();
    renderBatteryChart();
    renderActivityChart();
    renderFallEventsChart();
}

/**
 * Device Status Pie Chart
 */
function renderDeviceStatusChart() {
    const canvas = document.getElementById('deviceStatusChart');
    if (!canvas) return;
    
    const online = devicesData.filter(d => d.status === 'online').length;
    const offline = devicesData.filter(d => d.status === 'offline').length;
    const paired = devicesData.filter(d => d.isPaired).length;
    const unpaired = devicesData.filter(d => !d.isPaired).length;
    
    // Destroy existing chart
    if (charts.deviceStatus) {
        charts.deviceStatus.destroy();
    }
    
    charts.deviceStatus = new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: ['Online', 'Offline', 'Paired', 'Unpaired'],
            datasets: [{
                data: [online, offline, paired, unpaired],
                backgroundColor: [
                    '#48bb78',
                    '#f56565',
                    '#4299e1',
                    '#ed8936'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

/**
 * Battery Levels Bar Chart
 */
function renderBatteryChart() {
    const canvas = document.getElementById('batteryChart');
    if (!canvas) return;
    
    const deviceNames = devicesData.map(d => d.name || d.deviceId.substring(0, 10));
    const batteryLevels = devicesData.map(d => d.batteryLevel || 0);
    
    // Destroy existing chart
    if (charts.battery) {
        charts.battery.destroy();
    }
    
    charts.battery = new Chart(canvas, {
        type: 'bar',
        data: {
            labels: deviceNames,
            datasets: [{
                label: 'Battery Level (%)',
                data: batteryLevels,
                backgroundColor: batteryLevels.map(level => {
                    if (level > 60) return '#48bb78';
                    if (level > 30) return '#ed8936';
                    return '#f56565';
                }),
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

/**
 * Activity Timeline Line Chart
 */
function renderActivityChart() {
    const canvas = document.getElementById('activityChart');
    if (!canvas) return;
    
    // Generate mock data for last 24 hours
    const hours = [];
    const activities = [];
    
    for (let i = 23; i >= 0; i--) {
        const hour = new Date();
        hour.setHours(hour.getHours() - i);
        hours.push(hour.getHours() + ':00');
        activities.push(Math.floor(Math.random() * 100)); // Mock data
    }
    
    // Destroy existing chart
    if (charts.activity) {
        charts.activity.destroy();
    }
    
    charts.activity = new Chart(canvas, {
        type: 'line',
        data: {
            labels: hours,
            datasets: [{
                label: 'Sensor Data Points',
                data: activities,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

/**
 * Fall Events Bar Chart
 */
function renderFallEventsChart() {
    const canvas = document.getElementById('fallEventsChart');
    if (!canvas) return;
    
    // Generate mock data for last 7 days
    const days = [];
    const events = [];
    
    for (let i = 6; i >= 0; i--) {
        const day = new Date();
        day.setDate(day.getDate() - i);
        days.push(day.toLocaleDateString('en-US', { weekday: 'short' }));
        events.push(Math.floor(Math.random() * 5)); // Mock data
    }
    
    // Destroy existing chart
    if (charts.fallEvents) {
        charts.fallEvents.destroy();
    }
    
    charts.fallEvents = new Chart(canvas, {
        type: 'bar',
        data: {
            labels: days,
            datasets: [{
                label: 'Fall Events',
                data: events,
                backgroundColor: '#f56565',
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

/**
 * Render devices table
 */
function renderDevicesTable() {
    const container = document.getElementById('devicesTableContainer');
    if (!container) return;
    
    if (devicesData.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-microchip"></i>
                <h3>No Devices Yet</h3>
                <p>Add your first device to start monitoring</p>
                <a href="/devices" class="btn btn-primary">
                    <i class="fas fa-plus"></i> Add Device
                </a>
            </div>
        `;
        return;
    }
    
    const tableHTML = `
        <table class="devices-table">
            <thead>
                <tr>
                    <th>Device Name</th>
                    <th>Location</th>
                    <th>Status</th>
                    <th>Battery</th>
                    <th>Last Seen</th>
                </tr>
            </thead>
            <tbody>
                ${devicesData.map(device => `
                    <tr>
                        <td>
                            <strong>${device.name || 'Unnamed Device'}</strong><br>
                            <small style="color: #718096;">${device.deviceId}</small>
                        </td>
                        <td>${device.location || 'Not set'}</td>
                        <td>
                            <span class="status-badge ${device.status}">
                                ${device.status === 'online' ? '🟢' : '🔴'} ${device.status || 'offline'}
                            </span>
                        </td>
                        <td>
                            <div class="battery-bar">
                                <div class="battery-fill ${getBatteryClass(device.batteryLevel)}" 
                                     style="width: ${device.batteryLevel || 0}%"></div>
                            </div>
                            <small>${device.batteryLevel || 0}%</small>
                        </td>
                        <td>${formatTimestamp(device.lastSeen)}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    container.innerHTML = tableHTML;
}

/**
 * Render recent activity
 */
function renderRecentActivity() {
    const container = document.getElementById('activityListContainer');
    if (!container) return;
    
    // Mock recent activity data
    const activities = [
        {
            type: 'success',
            icon: 'fa-plug',
            title: 'Device Connected',
            description: devicesData[0]?.name || 'Device 1' + ' came online',
            time: '5 minutes ago'
        },
        {
            type: 'info',
            icon: 'fa-heartbeat',
            title: 'Heartbeat Received',
            description: 'All devices reporting normal status',
            time: '10 minutes ago'
        },
        {
            type: 'warning',
            icon: 'fa-battery-half',
            title: 'Low Battery Warning',
            description: devicesData[0]?.name || 'Device 1' + ' battery below 30%',
            time: '1 hour ago'
        },
        {
            type: 'info',
            icon: 'fa-microchip',
            title: 'Device Created',
            description: 'New device added to the system',
            time: '2 hours ago'
        }
    ];
    
    const activityHTML = `
        <div class="activity-list">
            ${activities.map(activity => `
                <div class="activity-item">
                    <div class="activity-icon ${activity.type}">
                        <i class="fas ${activity.icon}"></i>
                    </div>
                    <div class="activity-content">
                        <h4>${activity.title}</h4>
                        <p>${activity.description}</p>
                    </div>
                    <span class="activity-time">${activity.time}</span>
                </div>
            `).join('')}
        </div>
    `;
    
    container.innerHTML = activityHTML;
}

/**
 * Helper: Get battery class based on level
 */
function getBatteryClass(level) {
    if (level > 60) return 'high';
    if (level > 30) return 'medium';
    return 'low';
}

/**
 * Helper: Format timestamp
 */
function formatTimestamp(timestamp) {
    if (!timestamp) return 'Never';
    
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)} hours ago`;
    return date.toLocaleDateString();
}

console.log('✓ Dashboard script loaded');
