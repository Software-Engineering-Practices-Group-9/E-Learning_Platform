let tempVideos = [];
// 上傳影片到暫存
function uploadVideo() {
    const videoName = document.getElementById('video_name').value;
    const videoFile = document.getElementById('video_file').files[0];
    
    if (!videoName || !videoFile) {
        alert('請填寫影片名稱並選擇檔案');
        return;
    }
    
    const formData = new FormData();
    formData.append('video_file', videoFile);
    
    fetch('/create_course/temp_upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 儲存影片資訊
            tempVideos.push({
                temp_filename: data.temp_filename,
                video_name: videoName,
                thumbnail_url: data.thumbnail_url
            });
            
            // 更新隱藏欄位
            document.getElementById('videoData').value = JSON.stringify(tempVideos);
            
            // 更新影片列表顯示
            updateVideoList();
            
            // 關閉 Modal 並清空表單
            const modal = bootstrap.Modal.getInstance(document.getElementById('uploadVideoModal'));
            modal.hide();
            document.getElementById('video_name').value = '';
            document.getElementById('video_file').value = '';
        } else {
            alert('影片上傳失敗，請再試一次！');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('發生錯誤，請稍後再試！');
    });
}

// 更新影片列表顯示
function updateVideoList() {
    const videoList = document.getElementById('videoList');
    videoList.innerHTML = '';

    tempVideos.forEach((video, index) => {
        const card = document.createElement('div');
        card.className = 'col';

        card.innerHTML = `
            <div class="card">
                <img src="${video.thumbnail_url}" class="card-img-top" alt="${video.video_name}">
                <div class="card-body">
                    <h5 class="card-title">${video.video_name}</h5>
                    <button class="btn btn-danger btn-sm" onclick="deleteVideo(${index})">刪除</button>
                </div>
            </div>
        `;
        videoList.appendChild(card);
    });
}

// 刪除影片
function deleteVideo(index) {
    if (confirm('確定要刪除此影片嗎？')) {
        tempVideos.splice(index, 1);

        // 更新隱藏欄位
        document.getElementById('videoData').value = JSON.stringify(tempVideos);

        // 更新影片列表顯示
        updateVideoList();
    }
}