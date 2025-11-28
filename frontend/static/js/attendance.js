// Attendance Marking Logic
document.addEventListener('DOMContentLoaded', function() {
    const video = document.getElementById('webcam');
    const canvas = document.getElementById('canvas');
    const startBtn = document.getElementById('startAttendance');
    const cancelBtn = document.getElementById('cancelAttendance');
    const statusMsg = document.getElementById('statusMessage');
    const bleStatus = document.getElementById('bleStatus');
    const challengeText = document.getElementById('challengeText');
    const challengeStatus = document.getElementById('challengeStatus');
    const logContent = document.getElementById('logContent');
    const logsDiv = document.getElementById('verificationLogs');

    if (!video) return;  // Not on attendance page

    const camera = new CameraManager(video, canvas);
    let selectedSessionId = null;
    let attendanceInterval = null;
    let currentStep = 1;

    // Session selection
    document.querySelectorAll('.select-session-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            selectedSessionId = this.closest('.session-card').dataset.sessionId;
            document.querySelector('.session-selection').style.display = 'none';
            document.getElementById('attendanceProcess').style.display = 'block';
            statusMsg.textContent = 'Session selected. Ready to begin verification.';
            statusMsg.className = 'status-message';
        });
    });

    startBtn.addEventListener('click', async () => {
        if (!selectedSessionId) {
            statusMsg.textContent = 'Please select a session first.';
            statusMsg.className = 'status-message error';
            return;
        }

        try {
            await startAttendanceProcess();
        } catch (error) {
            statusMsg.textContent = 'Error: ' + error.message;
            statusMsg.className = 'status-message error';
            resetProcess();
        }
    });

    cancelBtn.addEventListener('click', () => {
        if (attendanceInterval) {
            clearInterval(attendanceInterval);
        }
        camera.stop();
        resetProcess();
    });

    function addLog(message, type='info') {
        logsDiv.style.display = 'block';
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.style.marginBottom = '5px';
        logEntry.style.color = type === 'error' ? 'red' : (type === 'success' ? 'green' : '#333');
        logEntry.innerHTML = `<strong>[${timestamp}]</strong> ${message}`;
        logContent.appendChild(logEntry);
        logsDiv.scrollTop = logsDiv.scrollHeight;
    }

    async function startAttendanceProcess() {
        statusMsg.textContent = 'Initializing camera...';
        addLog('Starting attendance process...');
        await camera.initialize();

        startBtn.style.display = 'none';
        cancelBtn.style.display = 'inline-block';
        
        // Clear previous logs
        logContent.innerHTML = '';
        logsDiv.style.display = 'none';

        // Unified verification process
        await performVerification();
    }

    async function performVerification() {
        currentStep = 1;
        statusMsg.textContent = 'Position your face in the camera and hold still...';
        bleStatus.textContent = 'Checking proximity...';
        bleStatus.className = 'status-indicator warning';
        addLog('Camera initialized. Capturing frame...');

        // Capture a frame after a short delay to allow positioning
        await new Promise(resolve => setTimeout(resolve, 2000));

        const frame = camera.captureFrame();
        
        statusMsg.textContent = 'Verifying identity and location...';
        addLog('Sending data to server for verification (BLE + Face)...');

        try {
            const response = await fetch('/student/api/mark-attendance', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: parseInt(selectedSessionId),
                    frame: frame,
                    liveness_challenge: null,  // Will be set if liveness is required
                    liveness_frames: []
                })
            });

            const result = await response.json();
            
            // Log BLE Details
            if (result.ble_details) {
                if (result.ble_details.verified) {
                    addLog(`BLE Success: Device found with RSSI ${result.ble_details.rssi}dBm`, 'success');
                } else {
                    addLog(`BLE Failed: ${result.ble_details.error || 'Signal too weak or device not found'} (RSSI: ${result.ble_details.rssi || 'N/A'})`, 'error');
                }
            } else {
                addLog('BLE Check: No details returned', 'error');
            }

            // Update BLE status based on real result
            if (result.ble_verified) {
                bleStatus.textContent = '✓ Within classroom range';
                bleStatus.className = 'status-indicator success';
            } else {
                bleStatus.textContent = '✗ Proximity check failed';
                bleStatus.className = 'status-indicator error';
            }

            if (result.success) {
                addLog('Face verification successful', 'success');
                if (result.liveness_verified) {
                    // Attendance marked successfully
                    statusMsg.textContent = '✓ Attendance marked successfully!';
                    statusMsg.className = 'status-message success';
                    setTimeout(() => {
                        window.location.href = '/student/dashboard';
                    }, 3000);
                } else {
                    // Liveness challenge required
                    document.getElementById('step3').style.display = 'block';
                    await performLivenessChallenge();
                }
            } else {
                if (result.errors && result.errors.length > 0) {
                    result.errors.forEach(err => addLog(`Verification Error: ${err}`, 'error'));
                    statusMsg.textContent = 'Error: ' + result.errors[0];
                } else {
                    addLog('Verification failed with unknown error', 'error');
                    statusMsg.textContent = 'Face verification failed. Please try again.';
                }
                statusMsg.className = 'status-message error';
                resetProcess();
            }
        } catch (error) {
            statusMsg.textContent = 'Error: ' + error.message;
            statusMsg.className = 'status-message error';
            resetProcess();
        }
    }

    async function performLivenessChallenge() {
        currentStep = 3;

        // Randomly select a challenge
        const challenges = ['blink', 'head_left', 'head_right'];
        const selectedChallenge = challenges[Math.floor(Math.random() * challenges.length)];

        let instruction = '';
        switch (selectedChallenge) {
            case 'blink':
                instruction = 'Please blink twice slowly';
                break;
            case 'head_left':
                instruction = 'Please turn your head to the left';
                break;
            case 'head_right':
                instruction = 'Please turn your head to the right';
                break;
        }

        challengeText.textContent = instruction;
        challengeStatus.textContent = 'Performing challenge...';
        challengeStatus.className = 'status-indicator warning';

        statusMsg.textContent = 'Performing liveness challenge...';

        // Capture frames for liveness verification
        const livenessFrames = [];
        const captureDuration = 3000; // 3 seconds
        const captureInterval = 200; // 200ms intervals

        const startTime = Date.now();
        attendanceInterval = setInterval(() => {
            if (Date.now() - startTime >= captureDuration) {
                clearInterval(attendanceInterval);
                completeLivenessChallenge(livenessFrames, selectedChallenge);
                return;
            }
            livenessFrames.push(camera.captureFrame());
        }, captureInterval);
    }

    async function completeLivenessChallenge(livenessFrames, challengeType) {
        try {
            const response = await fetch('/student/api/mark-attendance', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: parseInt(selectedSessionId),
                    frame: camera.captureFrame(), // Use latest frame
                    liveness_challenge: challengeType,
                    liveness_frames: livenessFrames
                })
            });

            const result = await response.json();

            if (result.success) {
                challengeStatus.textContent = '✓ Challenge completed';
                challengeStatus.className = 'status-indicator success';
                statusMsg.textContent = '✓ Attendance marked successfully!';
                statusMsg.className = 'status-message success';
                setTimeout(() => {
                    window.location.href = '/student/dashboard';
                }, 3000);
            } else {
                challengeStatus.textContent = '✗ Challenge failed';
                challengeStatus.className = 'status-indicator error';
                if (result.errors && result.errors.length > 0) {
                    statusMsg.textContent = 'Error: ' + result.errors[0];
                } else {
                    statusMsg.textContent = 'Liveness verification failed. Please try again.';
                }
                statusMsg.className = 'status-message error';
                resetProcess();
            }
        } catch (error) {
            challengeStatus.textContent = 'Error';
            challengeStatus.className = 'status-indicator error';
            statusMsg.textContent = 'Error: ' + error.message;
            statusMsg.className = 'status-message error';
            resetProcess();
        }
    }

    function resetProcess() {
        camera.stop();
        startBtn.style.display = 'inline-block';
        cancelBtn.style.display = 'none';
        document.getElementById('step3').style.display = 'none';

        // Reset status indicators
        bleStatus.textContent = 'Checking...';
        bleStatus.className = 'status-indicator';
        challengeStatus.textContent = 'Preparing...';
        challengeStatus.className = 'status-indicator';

        currentStep = 1;
    }
});
