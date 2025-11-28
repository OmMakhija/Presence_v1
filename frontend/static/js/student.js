// Face Registration Logic
document.addEventListener('DOMContentLoaded', function() {
    const video = document.getElementById('webcam');
    const canvas = document.getElementById('canvas');
    const startBtn = document.getElementById('startCapture');
    const cancelBtn = document.getElementById('cancelCapture');
    const statusMsg = document.getElementById('statusMessage');
    const progressContainer = document.querySelector('.progress-container');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');

    if (!video) return;  // Not on registration page

    const camera = new CameraManager(video, canvas);
    let captureInterval = null;
    let capturedFrames = [];

    const CAPTURE_DURATION = 10;  // seconds
    const CAPTURE_FPS = 10;
    const TOTAL_FRAMES = CAPTURE_DURATION * CAPTURE_FPS;

    startBtn.addEventListener('click', async () => {
        try {
            statusMsg.textContent = 'Initializing camera...';
            statusMsg.className = 'status-message';
            await camera.initialize();

            startBtn.style.display = 'none';
            cancelBtn.style.display = 'inline-block';
            progressContainer.style.display = 'block';

            capturedFrames = [];
            let frameCount = 0;

            captureInterval = setInterval(() => {
                const frame = camera.captureFrame();
                capturedFrames.push(frame);
                frameCount++;

                const progress = (frameCount / TOTAL_FRAMES) * 100;
                progressBar.style.width = progress + '%';
                progressText.textContent = `Capturing... ${frameCount}/${TOTAL_FRAMES}`;

                if (frameCount >= TOTAL_FRAMES) {
                    clearInterval(captureInterval);
                    finishCapture();
                }
            }, 1000 / CAPTURE_FPS);

        } catch (error) {
            statusMsg.textContent = 'Error: ' + error.message;
            statusMsg.className = 'status-message error';
        }
    });

    cancelBtn.addEventListener('click', () => {
        if (captureInterval) {
            clearInterval(captureInterval);
        }
        camera.stop();
        resetUI();
    });

    async function finishCapture() {
        camera.stop();
        progressText.textContent = 'Processing...';

        try {
            const response = await fetch('/student/api/register-face', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ frames: capturedFrames })
            });

            const result = await response.json();

            if (result.success) {
                statusMsg.textContent = '✓ Face registered successfully!';
                statusMsg.className = 'status-message success';
                setTimeout(() => {
                    window.location.href = '/student/dashboard';
                }, 2000);
            } else {
                statusMsg.textContent = 'Error: ' + result.error;
                statusMsg.className = 'status-message error';
                resetUI();
            }
        } catch (error) {
            statusMsg.textContent = 'Error: ' + error.message;
            statusMsg.className = 'status-message error';
            resetUI();
        }
    }

    function resetUI() {
        startBtn.style.display = 'inline-block';
        cancelBtn.style.display = 'none';
        progressContainer.style.display = 'none';
        progressBar.style.width = '0%';
        statusMsg.className = 'status-message';
    }
});
