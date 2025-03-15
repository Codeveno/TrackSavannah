function selectCamera(cameraName) {
    const cameraURL = getCameraURL(cameraName);

    if (cameraURL) {
        localStorage.setItem('selectedCameraURL', cameraURL);
        localStorage.setItem('selectedCameraName', cameraName);

        console.log(`Now Viewing: ${cameraName}`);

        if (cameraURL.includes("youtube")) {
            window.location.href = '/camera_feed';
        } else {
            window.location.href = `/video_feed/${encodeURIComponent(cameraName)}`;
        }
    } else {
        alert(`❌ Camera feed for '${cameraName}' not available.`);
    }
}

window.onload = function () {
    const cameraFeedElement = document.getElementById('camera-feed-container');
    const cameraTitleElement = document.getElementById('camera-title');
    const selectedCameraURL = localStorage.getItem('selectedCameraURL');
    const selectedCameraName = localStorage.getItem('selectedCameraName');

    if (cameraFeedElement && cameraTitleElement && selectedCameraURL) {
        if (selectedCameraURL.includes("youtube")) {
            cameraFeedElement.innerHTML = 
                `<iframe 
                    src="${selectedCameraURL}" 
                    width="90%" 
                    top="40px"
                    height="590px" 
                    frameborder="0" 
                    allowfullscreen>
                </iframe>`;
        } else {
            cameraFeedElement.innerHTML = 
                `<img src="${selectedCameraURL}" alt="${selectedCameraName}" width="100%" height="500px">`;
        }

        cameraTitleElement.textContent = selectedCameraName;
    } else if (cameraTitleElement) {
        cameraTitleElement.textContent = '❌ Camera Feed Not Available';
    }
};

function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    } else {
        console.error(`Section with ID '${sectionId}' not found.`);
    }
}

function getCameraURL(cameraName) {
    const cameraFeeds = {
        "Nkorho Bush Lodge": "https://www.youtube.com/embed/dIChLG4_WNs",
        "Rosie Pan": "https://www.youtube.com/embed/ItdXaWUVF48",
        "African Watering Hole": "https://www.youtube.com/embed/KyQAB-TKOVA",
        "Lisbon Falls": "https://www.youtube.com/embed/9viZIxuonrI",
        "OL DONYO": "https://www.youtube.com/embed/XsOU8JnEpNM",
        "Africam Show": "https://www.youtube.com/embed/a0BME_RcftQ",
        "Gorilla Forest Corridor": "https://www.youtube.com/embed/yfSyjwY6zSQ"
    };
    return cameraFeeds[cameraName] || null; 
}