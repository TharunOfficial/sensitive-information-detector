const loadingScreen = document.querySelector('.container');
const resultDiv = document.getElementById('result');
const sensitiveDataList = document.getElementById('sensitive-data-list');
const blurredImageContainer = document.getElementById('blurred-image-container');

document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();

   
    loadingScreen.style.display = 'block';
    loadingScreen.classList.add('loading');
    resultDiv.style.display = 'none'; 

    const formData = new FormData();
    formData.append('file', document.getElementById('file-input').files[0]);

    try {
       
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Network response was not ok.');

        const result = await response.json();

      
        sensitiveDataList.innerHTML = '';
        blurredImageContainer.innerHTML = '';

      
        if (result.sensitive_data.length > 0) {
            result.sensitive_data.forEach(([label, value]) => {
                const listItem = document.createElement('li');
                listItem.textContent = `${label}: ${value}`;
                sensitiveDataList.appendChild(listItem);
            });
        } else {
            sensitiveDataList.innerHTML = '<li>No sensitive data detected.</li>';
        }

    
        if (result.blurred_image_urls && result.blurred_image_urls.length > 0) {
            result.blurred_image_urls.forEach((url) => {
                const link = document.createElement('a');
                link.href = url;
                link.textContent = 'Download Blurred Image';
                link.target = '_blank';
                blurredImageContainer.appendChild(link);
                blurredImageContainer.appendChild(document.createElement('br'));
            });
        } else {
            blurredImageContainer.innerHTML = 'No blurred images available.';
        }

        
        setTimeout(() => {
            resultDiv.style.display = 'block';
            loadingScreen.style.display = 'none'; 
        }, 1800); 
    } catch (error) {
        console.error('Error:', error);
        alert('There was an error uploading the file.');

        
        setTimeout(() => {
            loadingScreen.classList.remove('loading');
            loadingScreen.style.display = 'none';
        }, 1800); 
    }
});
