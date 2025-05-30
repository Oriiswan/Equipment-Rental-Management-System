
  // Basic image upload preview functionality
  document.getElementById('equipment-image').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
      const preview = document.getElementById('image-preview');
      const thumbnail = document.getElementById('preview-thumbnail');
      const fileName = document.getElementById('file-name');
      const fileSize = document.getElementById('file-size');
      
      // Show preview
      preview.classList.remove('hidden');
      
      // Set thumbnail (create object URL)
      thumbnail.src = URL.createObjectURL(file);
      
      // Set file info
      fileName.textContent = file.name;
      fileSize.textContent = `${(file.size / (1024 * 1024)).toFixed(2)}MB`;
      
      // Clear URL input if file is selected
      document.getElementById('image-url').value = '';
    }
  });
