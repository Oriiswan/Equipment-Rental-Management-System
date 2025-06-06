
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

     Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
        Chart.defaults.color = '#4b5563';
        
        // Equipment Distribution Pie Chart
        const distributionCtx = document.getElementById('distributionChart').getContext('2d');
        new Chart(distributionCtx, {
            type: 'doughnut',
            data: {
                labels: ['Power Tools', 'Hand Tools', 'Safety Gear', 'Measuring', 'Other'],
                datasets: [{
                    data: [35, 25, 15, 15, 10],
                    backgroundColor: [
                        'rgba(99, 102, 241, 0.8)',
                        'rgba(139, 92, 246, 0.8)',
                        'rgba(236, 72, 153, 0.8)',
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(251, 191, 36, 0.8)'
                    ],
                    borderColor: [
                        'rgb(99, 102, 241)',
                        'rgb(139, 92, 246)',
                        'rgb(236, 72, 153)',
                        'rgb(16, 185, 129)',
                        'rgb(251, 191, 36)'
                    ],
                    borderWidth: 2,
                    hoverOffset: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    }
                },
                cutout: '60%'
            }
        });
        
        // Utilization Trends Line Chart
        const trendsCtx = document.getElementById('trendsChart').getContext('2d');
        new Chart(trendsCtx, {
            type: 'line',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'This Week'],
                datasets: [{
                    label: 'Utilization Rate',
                    data: [65, 72, 68, 78, 85],
                    borderColor: 'rgb(99, 102, 241)',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: 'rgb(99, 102, 241)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
        
        // Add hover effects and animations
        document.querySelectorAll('.utilization-item').forEach(item => {
            item.addEventListener('mouseenter', function() {
                this.style.transform = 'translateX(10px) scale(1.02)';
            });
            
            item.addEventListener('mouseleave', function() {
                this.style.transform = 'translateX(0) scale(1)';
            });
        });
        
        // Animate counters on load
        function animateCounters() {
            const counters = document.querySelectorAll('.stat-value');
            counters.forEach(counter => {
                const target = parseInt(counter.textContent);
                if (!isNaN(target)) {
                    let current = 0;
                    const increment = target / 30;
                    const timer = setInterval(() => {
                        current += increment;
                        if (current >= target) {
                            counter.textContent = target;
                            clearInterval(timer);
                        } else {
                            counter.textContent = Math.floor(current);
                        }
                    }, 50);
                }
            });
        }
        
        // Start animations when page loads
        window.addEventListener('load', () => {
            setTimeout(animateCounters, 500);
        });

