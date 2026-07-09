const API_BASE = '';

// ─────────────────────── Toast ───────────────────────
function showToast(message, type = 'info') {
    const icons = {
        success: 'fa-circle-check',
        error: 'fa-circle-exclamation',
        info: 'fa-circle-info',
    };
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="fa-solid ${icons[type]} toast-icon"></i>
        <span class="toast-message">${message}</span>
        <i class="fa-solid fa-xmark toast-close" onclick="this.parentElement.remove()"></i>
    `;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 5000);
}

// ─────────────────────── Tab Navigation ───────────────────────
const navItems = document.querySelectorAll('.nav-links li');
const tabContents = document.querySelectorAll('.tab-content');

navItems.forEach(item => {
    item.addEventListener('click', () => {
        navItems.forEach(n => n.classList.remove('active'));
        tabContents.forEach(t => t.classList.remove('active'));
        item.classList.add('active');
        const tabId = item.getAttribute('data-tab');
        document.getElementById(tabId).classList.add('active');
        if (tabId === 'dashboard-tab') {
            loadDashboard();
        }
    });
});

// ─────────────────────── Camera Utilities ───────────────────────
let registerStream = null;
let checkinStream = null;

async function startCamera(videoEl, streamRef) {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' },
            audio: false
        });
        videoEl.srcObject = stream;
        return stream;
    } catch (err) {
        let msg = 'Không thể truy cập camera.';
        if (err.name === 'NotAllowedError') msg = 'Bạn đã từ chối quyền camera. Vui lòng cấp quyền trong cài đặt trình duyệt.';
        else if (err.name === 'NotFoundError') msg = 'Không tìm thấy thiết bị camera.';
        showToast('❌ ' + msg, 'error');
        return null;
    }
}

function stopCamera(stream, videoEl) {
    if (stream) {
        stream.getTracks().forEach(t => t.stop());
        videoEl.srcObject = null;
    }
}

function captureFrame(videoEl, canvasEl) {
    canvasEl.width = videoEl.videoWidth;
    canvasEl.height = videoEl.videoHeight;
    canvasEl.getContext('2d').drawImage(videoEl, 0, 0);
    return new Promise(resolve => canvasEl.toBlob(resolve, 'image/jpeg', 0.92));
}

// ─────────────────────── Register ───────────────────────
const btnToggleRegisterCam = document.getElementById('btn-toggle-register-cam');
const btnStopRegisterCam = document.getElementById('btn-stop-register-cam');
const registerVideo = document.getElementById('register-video');
const registerCanvas = document.getElementById('register-canvas');
const registerCamOff = document.getElementById('register-cam-off');
const registerCamLive = document.getElementById('register-cam-live');
const registerCamStatus = document.getElementById('register-cam-status');
const btnRegister = document.getElementById('btn-register');

btnToggleRegisterCam.addEventListener('click', async () => {
    btnToggleRegisterCam.disabled = true;
    btnToggleRegisterCam.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang bật...';
    registerStream = await startCamera(registerVideo, registerStream);
    if (registerStream) {
        registerCamOff.style.display = 'none';
        registerCamLive.style.display = 'block';
        registerCamStatus.textContent = '🟢 Camera đang hoạt động';
    }
    btnToggleRegisterCam.disabled = false;
    btnToggleRegisterCam.innerHTML = '<i class="fa-solid fa-video"></i> Bật Camera';
});

btnStopRegisterCam.addEventListener('click', () => {
    stopCamera(registerStream, registerVideo);
    registerStream = null;
    registerCamLive.style.display = 'none';
    registerCamOff.style.display = 'flex';
});

btnRegister.addEventListener('click', async () => {
    const name = document.getElementById('register-name').value.trim();
    if (!name) {
        showToast('Vui lòng nhập họ và tên trước khi đăng ký!', 'error');
        return;
    }
    if (!registerStream) {
        showToast('Vui lòng bật camera trước khi đăng ký!', 'error');
        return;
    }

    btnRegister.disabled = true;
    btnRegister.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang chụp ảnh...';
    registerCamStatus.textContent = '📸 Đang chụp ảnh khuôn mặt...';

    try {
        const blob = await captureFrame(registerVideo, registerCanvas);
        const formData = new FormData();
        formData.append('name', name);
        formData.append('image', blob, 'face.jpg');

        const resp = await fetch(`${API_BASE}/users/register`, {
            method: 'POST',
            body: formData,
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.detail || 'Đăng ký thất bại');

        registerCamStatus.textContent = `✅ Đã đăng ký: ${data.name} (ID: ${data.id})`;
        document.getElementById('register-name').value = '';
        showToast(`✅ Đăng ký thành công! Nhân viên: <b>${data.name}</b> (ID: ${data.id})`, 'success');
    } catch (err) {
        registerCamStatus.textContent = '❌ Đăng ký thất bại';
        showToast(`❌ ${err.message}`, 'error');
    } finally {
        btnRegister.disabled = false;
        btnRegister.innerHTML = '<i class="fa-solid fa-user-check"></i> Đăng ký khuôn mặt';
        setTimeout(() => { registerCamStatus.textContent = '🟢 Camera đang hoạt động'; }, 2500);
    }
});

// ─────────────────────── Check-in ───────────────────────
const btnToggleCheckinCam = document.getElementById('btn-toggle-checkin-cam');
const btnStopCheckinCam = document.getElementById('btn-stop-checkin-cam');
const checkinVideo = document.getElementById('checkin-video');
const checkinCanvas = document.getElementById('checkin-canvas');
const checkinCamOff = document.getElementById('checkin-cam-off');
const checkinCamLive = document.getElementById('checkin-cam-live');
const checkinCamStatus = document.getElementById('checkin-cam-status');
const btnCheckin = document.getElementById('btn-checkin');

// Tạo Canvas để vẽ Bounding Box đè lên Video
let checkinOverlayCanvas = null;
let detectionIntervalId = null;

function setupOverlayCanvas() {
    if (!checkinOverlayCanvas) {
        checkinOverlayCanvas = document.createElement('canvas');
        checkinOverlayCanvas.style.position = 'absolute';
        checkinOverlayCanvas.style.top = '0';
        checkinOverlayCanvas.style.left = '0';
        checkinOverlayCanvas.style.width = '100%';
        checkinOverlayCanvas.style.height = '100%';
        checkinOverlayCanvas.style.pointerEvents = 'none';
        checkinOverlayCanvas.style.zIndex = '5';
        checkinVideo.parentElement.appendChild(checkinOverlayCanvas);
    }
}

function clearOverlay() {
    if (checkinOverlayCanvas) {
        const ctx = checkinOverlayCanvas.getContext('2d');
        ctx.clearRect(0, 0, checkinOverlayCanvas.width, checkinOverlayCanvas.height);
    }
}

async function startDetectionLoop() {
    setupOverlayCanvas();
    detectionIntervalId = setInterval(async () => {
        if (!checkinStream || checkinVideo.paused || checkinVideo.ended) return;

        // Chụp khung hình từ Video
        checkinCanvas.width = checkinVideo.videoWidth;
        checkinCanvas.height = checkinVideo.videoHeight;
        const ctxCanvas = checkinCanvas.getContext('2d');
        ctxCanvas.drawImage(checkinVideo, 0, 0);
        
        checkinOverlayCanvas.width = checkinVideo.videoWidth;
        checkinOverlayCanvas.height = checkinVideo.videoHeight;
        const ctxOverlay = checkinOverlayCanvas.getContext('2d');

        checkinCanvas.toBlob(async (blob) => {
            if (!blob) return;
            const formData = new FormData();
            formData.append('image', blob, 'detect.jpg');

            try {
                const resp = await fetch(`${API_BASE}/attendance/detect`, {
                    method: 'POST',
                    body: formData,
                });
                if (!resp.ok) return;
                const data = await resp.json(); // Trả về danh sách khuôn mặt kèm bbox, name, similarity

                ctxOverlay.clearRect(0, 0, checkinOverlayCanvas.width, checkinOverlayCanvas.height);
                
                data.faces.forEach(face => {
                    const [x1, y1, x2, y2] = face.bbox;
                    const isKnown = face.user_id !== null;
                    const label = isKnown ? `✓ ${face.name} (${face.score.toFixed(2)})` : '? Unknown';
                    const color = isKnown ? '#10b981' : '#ef4444';

                    // Vẽ bounding box (gương lật ngang nên ta xử lý gương ở tọa độ X)
                    ctxOverlay.strokeStyle = color;
                    ctxOverlay.lineWidth = 4;
                    
                    // Lật ngang tọa độ X do video bị lật scaleX(-1)
                    const w = checkinOverlayCanvas.width;
                    const rx1 = w - x2;
                    const rx2 = w - x1;

                    ctxOverlay.strokeRect(rx1, y1, rx2 - rx1, y2 - y1);

                    // Vẽ label
                    ctxOverlay.fillStyle = color;
                    ctxOverlay.font = 'bold 20px Inter, sans-serif';
                    const textWidth = ctxOverlay.measureText(label).width;
                    ctxOverlay.fillRect(rx1, y1 - 32 > 0 ? y1 - 32 : y1, textWidth + 15, 30);

                    ctxOverlay.fillStyle = '#ffffff';
                    ctxOverlay.fillText(label, rx1 + 8, y1 - 32 > 0 ? y1 - 10 : y1 + 22);
                });
            } catch (err) {
                // Lỗi im lặng do là loop detection liên tục
            }
        }, 'image/jpeg', 0.5); // Giảm chất lượng ảnh quét liên tục để tối ưu hiệu năng
    }, 400); // Quét mỗi 400ms
}

function stopDetectionLoop() {
    if (detectionIntervalId) {
        clearInterval(detectionIntervalId);
        detectionIntervalId = null;
    }
    clearOverlay();
}

btnToggleCheckinCam.addEventListener('click', async () => {
    btnToggleCheckinCam.disabled = true;
    btnToggleCheckinCam.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang bật...';
    checkinStream = await startCamera(checkinVideo, checkinStream);
    if (checkinStream) {
        checkinCamOff.style.display = 'none';
        checkinCamLive.style.display = 'block';
        checkinCamStatus.textContent = '🟢 Sẵn sàng điểm danh';
        // Bắt đầu vòng lặp detect
        startDetectionLoop();
    }
    btnToggleCheckinCam.disabled = false;
    btnToggleCheckinCam.innerHTML = '<i class="fa-solid fa-video"></i> Bật Camera';
});

btnStopCheckinCam.addEventListener('click', () => {
    stopCamera(checkinStream, checkinVideo);
    checkinStream = null;
    stopDetectionLoop();
    checkinCamLive.style.display = 'none';
    checkinCamOff.style.display = 'flex';
});

btnCheckin.addEventListener('click', async () => {
    if (!checkinStream) {
        showToast('Vui lòng bật camera trước khi điểm danh!', 'error');
        return;
    }

    btnCheckin.disabled = true;
    btnCheckin.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang nhận diện...';
    checkinCamStatus.textContent = '📸 Đang chụp & nhận diện khuôn mặt...';

    try {
        const blob = await captureFrame(checkinVideo, checkinCanvas);
        const formData = new FormData();
        formData.append('image', blob, 'face.jpg');

        const resp = await fetch(`${API_BASE}/attendance/check-in`, {
            method: 'POST',
            body: formData,
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.detail || 'Check-in thất bại');

        const checkinTime = new Date(data.check_in).toLocaleString('vi-VN');
        const userName = data.user ? data.user.name : `ID ${data.user_id}`;
        checkinCamStatus.textContent = `✅ Điểm danh: ${userName} lúc ${checkinTime}`;
        showToast(`✅ <b>${userName}</b> đã điểm danh thành công lúc ${checkinTime}`, 'success');
    } catch (err) {
        checkinCamStatus.textContent = '❌ Không thể điểm danh';
        showToast(`❌ ${err.message}`, 'error');
    } finally {
        btnCheckin.disabled = false;
        btnCheckin.innerHTML = '<i class="fa-solid fa-expand"></i> Quét khuôn mặt điểm danh';
        setTimeout(() => { checkinCamStatus.textContent = '🟢 Sẵn sàng điểm danh'; }, 3000);
    }
});


// ─────────────────────── Dashboard ───────────────────────
let attendanceChart = null;

async function loadDashboard() {
    document.getElementById('stat-total-users').textContent = '...';
    document.getElementById('stat-today-checkins').textContent = '...';
    document.getElementById('stat-attendance-rate').textContent = '...';

    try {
        const [usersResp, attendancesResp] = await Promise.all([
            fetch(`${API_BASE}/users/`),
            fetch(`${API_BASE}/attendance/`),
        ]);

        if (!usersResp.ok || !attendancesResp.ok) {
            throw new Error('Không thể tải dữ liệu từ server');
        }

        const users = await usersResp.json();
        const attendances = await attendancesResp.json();

        renderStats(users, attendances);
        renderUsersTable(users);
        renderLogsTable(attendances);
        renderChart(users, attendances);
    } catch (err) {
        showToast(`❌ Dashboard: ${err.message}`, 'error');
    }
}

function getTodayDateStr() {
    return new Date().toISOString().split('T')[0];
}

function renderStats(users, attendances) {
    const today = getTodayDateStr();
    const todayAttendances = attendances.filter(a => {
        const d = new Date(a.check_in).toISOString().split('T')[0];
        return d === today;
    });

    const totalUsers = users.length;
    const todayCount = todayAttendances.length;
    const rate = totalUsers > 0 ? Math.round((todayCount / totalUsers) * 100) : 0;

    document.getElementById('stat-total-users').textContent = totalUsers;
    document.getElementById('stat-today-checkins').textContent = todayCount;
    document.getElementById('stat-attendance-rate').textContent = `${rate}%`;
}

function renderUsersTable(users) {
    document.getElementById('user-count').textContent = users.length;
    const tbody = document.getElementById('users-table-body');
    if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted">Chưa có nhân viên nào đăng ký</td></tr>';
        return;
    }
    tbody.innerHTML = users.map(u => `
        <tr>
            <td>#${u.id}</td>
            <td><b>${u.name}</b></td>
            <td class="text-muted" style="font-size:0.8rem;">${u.embedding_path}</td>
        </tr>
    `).join('');
}

function renderLogsTable(attendances) {
    const today = getTodayDateStr();
    const todayLogs = attendances.filter(a => {
        const d = new Date(a.check_in).toISOString().split('T')[0];
        return d === today;
    }).sort((a, b) => new Date(b.check_in) - new Date(a.check_in));

    const tbody = document.getElementById('logs-table-body');
    if (todayLogs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">Chưa có check-in nào hôm nay</td></tr>';
        return;
    }
    tbody.innerHTML = todayLogs.map(a => {
        const name = a.user ? a.user.name : `User ${a.user_id}`;
        const time = new Date(a.check_in).toLocaleTimeString('vi-VN');
        return `
            <tr>
                <td>${time}</td>
                <td><b>${name}</b></td>
                <td>#${a.user_id}</td>
                <td><span class="badge badge-success"><i class="fa-solid fa-check"></i> Thành công</span></td>
            </tr>
        `;
    }).join('');
}

function renderChart(users, attendances) {
    // Group attendances by hour of today
    const today = getTodayDateStr();
    const hourCounts = Array(24).fill(0);
    attendances.forEach(a => {
        const date = new Date(a.check_in);
        const dateStr = date.toISOString().split('T')[0];
        if (dateStr === today) {
            hourCounts[date.getHours()]++;
        }
    });

    const labels = Array.from({ length: 24 }, (_, i) => `${String(i).padStart(2, '0')}:00`);

    const ctx = document.getElementById('attendance-chart').getContext('2d');

    if (attendanceChart) {
        attendanceChart.destroy();
    }

    attendanceChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Số lần check-in',
                data: hourCounts,
                backgroundColor: 'rgba(59, 130, 246, 0.5)',
                borderColor: 'rgba(59, 130, 246, 1)',
                borderWidth: 2,
                borderRadius: 6,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    borderColor: 'rgba(59, 130, 246, 0.3)',
                    borderWidth: 1,
                    titleColor: '#f8fafc',
                    bodyColor: '#94a3b8',
                    callbacks: {
                        label: (ctx) => ` ${ctx.parsed.y} check-in`,
                    },
                },
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255,255,255,0.04)' },
                    ticks: { color: '#94a3b8', font: { size: 10 } },
                },
                y: {
                    grid: { color: 'rgba(255,255,255,0.04)' },
                    ticks: { color: '#94a3b8', stepSize: 1 },
                    beginAtZero: true,
                },
            },
        },
    });
}

// Refresh button
document.getElementById('btn-refresh-dashboard').addEventListener('click', () => {
    loadDashboard();
    showToast('Đã làm mới dữ liệu Dashboard', 'info');
});
