// LibraSync — Main JavaScript

// Auto-dismiss flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', () => {
  const flashMsgs = document.querySelectorAll('.flash-msg');
  flashMsgs.forEach(msg => {
    setTimeout(() => {
      msg.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
      msg.style.opacity = '0';
      msg.style.transform = 'translateY(-8px)';
      setTimeout(() => msg.remove(), 400);
    }, 5000);
  });

  // Mark notifications as read if on student pages
  const markReadBtn = document.getElementById('mark-read');
  if (markReadBtn) {
    fetch('/student/notifications/mark_read', { method: 'POST' });
  }

  // File upload preview
  const imageInput = document.getElementById('imageInput');
  if (imageInput) {
    imageInput.addEventListener('change', function () {
      if (this.files[0]) {
        const preview = document.getElementById('imagePreview');
        if (preview) {
          preview.src = URL.createObjectURL(this.files[0]);
          preview.style.display = 'block';
        }
      }
    });
  }
});

// Close modals when clicking overlay
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.style.display = 'none';
  }
});

// Keyboard shortcut — Escape to close modal
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay').forEach(m => m.style.display = 'none');
  }
});
