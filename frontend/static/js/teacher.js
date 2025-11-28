// Teacher Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Modal functionality
    const modal = document.getElementById('createSessionModal');
    const createBtn = document.getElementById('createSessionBtn');
    const closeBtn = document.querySelector('.close');

    if (createBtn && modal) {
        createBtn.addEventListener('click', function() {
            modal.style.display = 'block';
        });

        closeBtn.addEventListener('click', function() {
            modal.style.display = 'none';
        });

        window.addEventListener('click', function(event) {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    }

    // Create session form
    const createForm = document.getElementById('createSessionForm');
    if (createForm) {
        createForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            const sessionData = {
                course_code: formData.get('course_code'),
                course_name: formData.get('course_name'),
                session_date: formData.get('session_date'),
                start_time: formData.get('start_time'),
                end_time: formData.get('end_time'),
                is_active: formData.get('is_active') === 'on'
            };

            try {
                const response = await fetch('/teacher/api/create-session', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(sessionData)
                });

                const result = await response.json();

                if (result.success) {
                    alert('Session created successfully!');
                    modal.style.display = 'none';
                    location.reload(); // Refresh to show new session
                } else {
                    alert('Error creating session: ' + result.error);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        });
    }

    // Toggle session active/inactive
    document.querySelectorAll('.toggle-session-btn').forEach(btn => {
        btn.addEventListener('click', async function() {
            const sessionId = this.dataset.sessionId;
            const isCurrentlyActive = this.classList.contains('btn-danger');

            try {
                const response = await fetch(`/teacher/api/toggle-session/${sessionId}`, {
                    method: 'POST'
                });

                const result = await response.json();

                if (result.success) {
                    // Update button appearance
                    if (result.is_active) {
                        this.classList.remove('btn-success');
                        this.classList.add('btn-danger');
                        this.textContent = 'Deactivate';
                    } else {
                        this.classList.remove('btn-danger');
                        this.classList.add('btn-success');
                        this.textContent = 'Activate';
                    }

                    // Update status badge
                    const statusBadge = this.closest('.session-card').querySelector('.status-badge');
                    if (result.is_active) {
                        statusBadge.classList.add('active');
                        statusBadge.classList.remove('inactive');
                        statusBadge.textContent = 'Active';
                    } else {
                        statusBadge.classList.remove('active');
                        statusBadge.classList.add('inactive');
                        statusBadge.textContent = 'Inactive';
                    }
                } else {
                    alert('Error toggling session status');
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        });
    });

    // Delete session
    document.querySelectorAll('.delete-session-btn').forEach(btn => {
        btn.addEventListener('click', async function() {
            if (!confirm('Are you sure you want to delete this session? This action cannot be undone and will remove all associated attendance records.')) {
                return;
            }

            const sessionId = this.dataset.sessionId;

            try {
                const response = await fetch(`/teacher/api/delete-session/${sessionId}`, {
                    method: 'DELETE'
                });

                const result = await response.json();

                if (result.success) {
                    alert('Session deleted successfully');
                    location.reload();
                } else {
                    alert('Error deleting session: ' + result.error);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        });
    });
});
