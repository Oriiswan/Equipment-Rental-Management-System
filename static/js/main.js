
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

  const dropdownButton = document.getElementById('dropdownButton');
        const dropdownMenu = document.getElementById('dropdownMenu');
        const chevron = document.getElementById('chevron');
        const selectedText = document.getElementById('selectedText');
        const dropdownItems = document.querySelectorAll('.dropdown-item');

        let isOpen = false;
        let selectedValue = 'newest';

        const sortLabels = {
            'newest': 'Newest First',
            'oldest': 'Oldest First',
            'today': 'Today',
            'week': 'This Week',
            'month': 'This Month',
            'year': 'This Year'
        };

        // Toggle dropdown
        dropdownButton.addEventListener('click', () => {
            isOpen = !isOpen;
            dropdownMenu.classList.toggle('hidden', !isOpen);
            chevron.classList.toggle('rotate-180', isOpen);
        });

        // Handle item selection
        dropdownItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                
                // Remove active state from all items
                dropdownItems.forEach(i => {
                    i.classList.remove('bg-blue-50', 'text-blue-700');
                    i.classList.add('text-gray-700');
                    const dot = i.querySelector('.w-2.h-2');
                    if (dot) dot.remove();
                });
                
                // Add active state to selected item
                item.classList.add('bg-blue-50', 'text-blue-700');
                item.classList.remove('text-gray-700');
                const dot = document.createElement('div');
                dot.className = 'ml-auto w-2 h-2 bg-blue-600 rounded-full';
                item.appendChild(dot);
                
                // Update selected value and text
                selectedValue = item.dataset.value;
                selectedText.textContent = `Sort by Date: ${sortLabels[selectedValue]}`;
                
                // Close dropdown
                isOpen = false;
                dropdownMenu.classList.add('hidden');
                chevron.classList.remove('rotate-180');
                
                console.log('Selected sort:', selectedValue);
            });
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!dropdownButton.contains(e.target) && !dropdownMenu.contains(e.target)) {
                isOpen = false;
                dropdownMenu.classList.add('hidden');
                chevron.classList.remove('rotate-180');
            }
        });

        document.addEventListener('DOMContentLoaded', function() {
    // When modal opens
    document.body.style.overflow = 'hidden';
    
    // When modal closes (either via confirm or cancel)
    function closeModal() {
        document.body.style.overflow = '';
    }
    
    // Attach to cancel button
    document.querySelector('a[href="/booking/list/"]').addEventListener('click', closeModal);
        })

  