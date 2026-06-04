document.addEventListener('DOMContentLoaded', function() {
    // Image preview functionality
    function previewImage(input, previewDiv) {
        previewDiv.innerHTML = '';
        if (input.files && input.files[0]) {
            const file = input.files[0];
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.style.maxWidth = '300px';
                    img.style.borderRadius = '10px';
                    previewDiv.appendChild(img);
                };
                reader.readAsDataURL(file);
            }
        }
    }

    // Preview generated/styled images
    function previewResult(url, previewDiv) {
        previewDiv.innerHTML = '';
        const img = document.createElement('img');
        img.src = url;
        img.style.maxWidth = '100%';
        img.style.borderRadius = '10px';
        img.style.margin = '15px 0';
        previewDiv.appendChild(img);

        // Add download link
        const downloadLink = document.createElement('a');
        downloadLink.href = url;
        downloadLink.download = '';
        downloadLink.textContent = 'Download Image';
        downloadLink.style.display = 'inline-block';
        downloadLink.style.marginTop = '10px';
        downloadLink.style.padding = '10px 20px';
        downloadLink.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
        downloadLink.style.color = 'white';
        downloadLink.style.textDecoration = 'none';
        downloadLink.style.borderRadius = '5px';
        previewDiv.appendChild(downloadLink);
    }

    // Event listener for stylize file input
    document.getElementById('stylize-file').addEventListener('change', function() {
        previewImage(this, document.getElementById('stylize-preview'));
    });

    // Generate image from prompt
    document.getElementById('generate-btn').addEventListener('click', function() {
        const prompt = document.getElementById('generate-prompt').value.trim();
        if (!prompt) {
            alert('Please enter a text prompt.');
            return;
        }

        const btn = this;
        const progressDiv = document.getElementById('generate-progress');
        const previewDiv = document.getElementById('generated-preview');

        // Disable button and show progress
        btn.disabled = true;
        btn.textContent = 'Generating...';
        progressDiv.style.display = 'block';
        progressDiv.textContent = 'Generating image from prompt...';

        fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: prompt })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
            } else {
                previewResult(data.image_url, previewDiv);
                // Refresh gallery after new image is generated
                loadGallery();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while generating the image.');
        })
        .finally(() => {
            // Re-enable button and hide progress
            btn.disabled = false;
            btn.textContent = 'Generate Image';
            progressDiv.style.display = 'none';
        });
    });

    // Stylize form submission
    document.getElementById('stylizeForm').addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(this);
        const resultDiv = document.getElementById('result');
        const submitBtn = document.getElementById('stylize-btn');
        const progressDiv = document.getElementById('stylize-progress');
        const previewDiv = document.getElementById('stylized-preview');

        // Disable button and show loading
        submitBtn.disabled = true;
        submitBtn.textContent = 'Stylizing...';
        progressDiv.style.display = 'block';
        progressDiv.textContent = 'Applying style transformation...';

        // Clear previous results
        resultDiv.innerHTML = '';

        // Send POST request to /stylize
        fetch('/stylize', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                resultDiv.innerHTML = `<p class="error">${data.error}</p>`;
            } else {
                previewResult(data.image_url, previewDiv);
                // Refresh gallery after new image is generated
                loadGallery();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            resultDiv.innerHTML = '<p class="error">An error occurred. Please try again.</p>';
        })
        .finally(() => {
            // Re-enable button
            submitBtn.disabled = false;
            submitBtn.textContent = 'Apply Style';
            progressDiv.style.display = 'none';
        });
    });

    // Gallery functionality
    function loadGallery() {
        const galleryDiv = document.getElementById('gallery');
        galleryDiv.innerHTML = '<p>Loading gallery...</p>';

        fetch('/gallery')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                galleryDiv.innerHTML = `<p class="error">${data.error}</p>`;
                return;
            }

            if (data.images.length === 0) {
                galleryDiv.innerHTML = '<p>No images generated yet. Create some images to see them here!</p>';
                return;
            }

            galleryDiv.innerHTML = '';
            data.images.forEach(image => {
                const imageCard = document.createElement('div');
                imageCard.className = 'gallery-item';

                const img = document.createElement('img');
                img.src = image.url;
                img.alt = image.filename;
                img.style.width = '100%';
                img.style.height = '200px';
                img.style.objectFit = 'cover';
                img.style.borderRadius = '10px';

                const downloadBtn = document.createElement('a');
                downloadBtn.href = image.url;
                downloadBtn.download = image.filename;
                downloadBtn.textContent = 'Download';
                downloadBtn.className = 'download-btn';
                downloadBtn.style.display = 'inline-block';
                downloadBtn.style.marginTop = '10px';
                downloadBtn.style.padding = '8px 16px';
                downloadBtn.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                downloadBtn.style.color = 'white';
                downloadBtn.style.textDecoration = 'none';
                downloadBtn.style.borderRadius = '5px';
                downloadBtn.style.fontSize = '14px';

                imageCard.appendChild(img);
                imageCard.appendChild(downloadBtn);
                galleryDiv.appendChild(imageCard);
            });
        })
        .catch(error => {
            console.error('Error loading gallery:', error);
            galleryDiv.innerHTML = '<p class="error">Failed to load gallery.</p>';
        });
    }

    // Refresh gallery button
    document.getElementById('refresh-gallery-btn').addEventListener('click', function() {
        loadGallery();
    });

    // Load gallery on page load
    loadGallery();
});
