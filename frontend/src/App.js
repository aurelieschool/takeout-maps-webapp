const formData = new FormData();
formData.append('file', myFileInput.files[0])

fetch('/locations', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log(data);
})
.catch(error => {
    console.error('Error:', error);
});