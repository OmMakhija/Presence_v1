// Session Detail Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Export attendance CSV
    const exportBtn = document.getElementById('exportBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', async function() {
            const sessionId = this.dataset.sessionId;

            try {
                const response = await fetch(`/teacher/api/export-attendance/${sessionId}`);

                if (response.ok) {
                    // Create download link
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;

                    // Get filename from response headers
                    const contentDisposition = response.headers.get('Content-Disposition');
                    let filename = 'attendance.csv';
                    if (contentDisposition) {
                        const matches = contentDisposition.match(/filename="(.+)"/);
                        if (matches) filename = matches[1];
                    }

                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                } else {
                    alert('Error exporting attendance data');
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        });
    }

    // Manual attendance override
    document.querySelectorAll('.update-btn').forEach(btn => {
        btn.addEventListener('click', async function() {
            const row = this.closest('tr');
            const studentId = row.dataset.studentId;
            const sessionId = row.dataset.sessionId;
            const statusSelect = row.querySelector('.status-select');
            const newStatus = statusSelect.value;

            // Confirm the change
            if (!confirm(`Are you sure you want to change this student's attendance to "${newStatus}"?`)) {
                return;
            }

            try {
                const response = await fetch('/teacher/api/manual-override', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        user_id: parseInt(studentId),
                        session_id: parseInt(sessionId),
                        status: newStatus,
                        notes: 'Manual override by teacher'
                    })
                });

                const result = await response.json();

                if (result.success) {
                    // Update the status display
                    const statusSpan = row.querySelector('.status-present, .status-absent, .status-proxy_suspected');
                    if (statusSpan) {
                        statusSpan.className = `status-${newStatus}`;
                        statusSpan.textContent = newStatus.charAt(0).toUpperCase() + newStatus.slice(1).replace('_', ' ');
                    }

                    // Update attendance summary stats
                    updateAttendanceStats();

                    alert('Attendance updated successfully!');
                } else {
                    alert('Error updating attendance: ' + (result.error || 'Unknown error'));
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        });
    });

    function updateAttendanceStats() {
        // This would require re-fetching the data or updating counters
        // For now, we'll just reload the page to show updated stats
        // In a production app, you'd update the counters dynamically
        location.reload();
    }
});
