class FatigueDetectionApp {
    constructor() {
        this.updateInterval = 500;
        this.init();
    }

    init() {
        this.startDataUpdates();
        console.log('Fatigue Detection App initialized');
    }

    async updateFatigueData() {
        try {
            const response = await fetch('/api/fatigue_data');
            const data = await response.json();
            
            this.updateFatigueLevel(data);
            this.updateStats(data);
            this.updateIndicators(data);
            this.updateAlerts(data);
        } catch (error) {
            console.error('Error fetching fatigue data:', error);
        }
    }

    updateFatigueLevel(data) {
        const levelText = document.getElementById('level-text');
        const levelScore = document.getElementById('level-score');
        const progressFill = document.getElementById('progress-fill');
        const statusBadge = document.getElementById('status-badge');

        levelText.textContent = data.fatigue_level;
        levelScore.textContent = `${data.fatigue_score}/100`;

        const progress = data.fatigue_score;
        progressFill.style.width = `${progress}%`;

        let levelClass = '';
        let badgeClass = '';
        let badgeText = '正常';

        switch (data.fatigue_level) {
            case 'Normal':
                levelClass = '';
                badgeClass = '';
                badgeText = '正常';
                break;
            case 'Mild Fatigue':
                levelClass = 'warning';
                badgeClass = 'warning';
                badgeText = '轻度疲劳';
                break;
            case 'Moderate Fatigue':
                levelClass = 'warning';
                badgeClass = 'warning';
                badgeText = '中度疲劳';
                break;
            case 'Severe Fatigue':
                levelClass = 'danger';
                badgeClass = 'danger';
                badgeText = '重度疲劳';
                break;
        }

        progressFill.className = 'progress-fill';
        if (levelClass) {
            progressFill.classList.add(levelClass);
        }

        statusBadge.className = 'status-badge';
        if (badgeClass) {
            statusBadge.classList.add(badgeClass);
        }
        statusBadge.textContent = badgeText;
    }

    updateStats(data) {
        document.getElementById('total-blinks').textContent = data.total_blinks;
        document.getElementById('yawn-count').textContent = data.yawn_count;
        document.getElementById('blink-rate').textContent = `${data.blink_rate.toFixed(1)} /min`;
        document.getElementById('eye-closed').textContent = `${data.eye_closed_duration.toFixed(1)}s`;
        document.getElementById('runtime').textContent = data.runtime;
        document.getElementById('fps').textContent = data.fps;
    }

    updateIndicators(data) {
        document.getElementById('ear-value').textContent = data.ear.toFixed(3);
        document.getElementById('mar-value').textContent = data.mar.toFixed(3);
    }

    updateAlerts(data) {
        const fatigueAlert = document.getElementById('fatigue-alert');
        const yawnAlert = document.getElementById('yawn-alert');

        if (data.is_fatigued) {
            fatigueAlert.classList.add('active');
        } else {
            fatigueAlert.classList.remove('active');
        }

        if (data.is_yawning) {
            yawnAlert.classList.add('active');
        } else {
            yawnAlert.classList.remove('active');
        }
    }

    startDataUpdates() {
        setInterval(() => {
            this.updateFatigueData();
        }, this.updateInterval);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new FatigueDetectionApp();
});
