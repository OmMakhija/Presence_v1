// Camera utility functions
class CameraManager {
    constructor(videoElement, canvasElement) {
        this.video = videoElement;
        this.canvas = canvasElement;
        this.stream = null;
        this.isInitialized = false;
    }

    async initialize() {
        if (this.isInitialized) return true;

        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480, facingMode: 'user' }
            });
            this.video.srcObject = this.stream;

            return new Promise((resolve) => {
                this.video.onloadedmetadata = () => {
                    this.video.play();
                    this.isInitialized = true;
                    resolve(true);
                };
            });
        } catch (error) {
            console.error('Camera access error:', error);
            throw new Error('Could not access camera. Please ensure camera permissions are granted.');
        }
    }

    stop() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
            this.isInitialized = false;
        }
    }

    captureFrame() {
        const context = this.canvas.getContext('2d');
        this.canvas.width = this.video.videoWidth;
        this.canvas.height = this.video.videoHeight;
        context.drawImage(this.video, 0, 0);
        return this.canvas.toDataURL('image/jpeg', 0.8);
    }

    isActive() {
        return this.stream && this.stream.active;
    }
}
