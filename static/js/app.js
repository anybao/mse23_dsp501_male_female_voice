let likedGirls = [];
let currentGirlId = null;

// Handle the "Like" button click
function handleLike() {
    const girlId = document.getElementById('girl-id').value;
    const girlName = document.getElementById('girl-name').textContent;

    // Add girl to liked list
    likedGirls.push({id: girlId, name: girlName});


    // Save the liked girl to the cookie
    saveGirlToCookie(girlId, girlName);

    const cardElement = document.querySelector('.card');
    cardElement.classList.add('like-animation'); // Add the like animation class

    // Wait for the animation to complete before fetching a new girl
    cardElement.addEventListener('animationend', () => {
        cardElement.classList.remove('like-animation'); // Remove the animation class
        const girlId = document.getElementById('girl-id').value; // Get current girl ID
        saveIdToCookie('liked_girl_ids', girlId); // Save the liked girl ID
        fetchGirl('/like', 'POST');
    }, {once: true}); // Ensure the event listener runs only once
}

// Handle the "Pass" button click
function handlePass() {
    const cardElement = document.querySelector('.card');
    cardElement.classList.add('pass-animation'); // Add the animation class

    // Wait for the animation to complete before fetching a new girl
    cardElement.addEventListener('animationend', () => {
        cardElement.classList.remove('pass-animation'); // Remove the animation class
        const girlId = document.getElementById('girl-id').value; // Get current girl ID
        saveIdToCookie('passed_girl_ids', girlId); // Save the passed girl ID
        fetchGirl('/pass', 'POST');
    }, {once: true}); // Ensure the event listener runs only once
}

// Fetch new girl data and update the UI
function fetchGirl(endpoint, method, body = null) {
    const likedIds = getCookie('liked_girl_ids') || '';
    const passedIds = getCookie('passed_girl_ids') || '';

    // Exclude already liked and passed girls
    const excludeIds = [...new Set([...likedIds.split(','), ...passedIds.split(',')])].filter(Boolean);

    if (body === null) {
        body = JSON.stringify({
            exclude_ids: excludeIds, // Send exclude list of IDs
        })
    }

    if (endpoint === '/like') {
        const girlId = document.getElementById('girl-id').value;
        body = JSON.stringify({
            exclude_ids: excludeIds, // Send exclude list of IDs
            current_girl_id: girlId,
            liked_ids: likedIds.split(','),
        })
    }

    fetch(endpoint, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: body
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then((data) => {
            model = data.model
            currentGirlId = model.id;  // Save the current girl's ID

            // Update image
            const imageElement = document.getElementById('girl-image');
            imageElement.src = `/static/images/models/${model.id}.jpg`;
            imageElement.alt = model.name;

            // Update name
            const nameElement = document.getElementById('girl-name');
            nameElement.textContent = model.name;
            nameElement.href = model.link;

            // Update girl id
            const girlId = document.getElementById('girl-id');
            girlId.value = model.id;

            // Update girl id
            const confidenceLevel = document.getElementById('confidence-level');
            if (data?.suggestion?.confidence !== undefined) {
                confidenceLevel.textContent = `(Confidence Level: ${(data.suggestion.confidence * 100).toFixed(2)}%)`;
            } else {
                confidenceLevel.textContent = '';
            }

            // Update details
            const detailsElement = document.querySelector('.details');
            const detailsHTML = generateDetailsHTML(model);
            detailsElement.innerHTML = detailsHTML;
        })
        .catch((error) => {
            console.error('Error fetching new girl data:', error);
        });
}

// Generate HTML for details dynamically
function generateDetailsHTML(girl) {
    const details = [
        {label: 'Born', value: girl.born},
        {label: 'Measurements', value: girl.measurements},
        {label: 'Cup Size', value: girl.cup_size},
        {label: 'AV Activity', value: girl.av_activity},
    ];

    return details
        .filter((item) => item.value && !item.value.includes('n/a'))
        .map((item) => `<p><strong>${item.label}:</strong> ${item.value}</p>`)
        .join('');
}

// Generate HTML for details dynamically
function generateFullDetailsHTML(girl) {
    const details = [
        {label: 'Born', value: girl.born},
        {label: 'Measurements', value: girl.measurements},
        {label: 'Cup Size', value: girl.cup_size},
        {label: 'AV Activity', value: girl.av_activity},
        {label: 'Sign', value: girl.sign},
        {label: 'Blood Type', value: girl.blood_type},
        {label: 'Height', value: girl.height},
        // { label: 'Nationality', value: girl.nationality },
    ];

    return details
        .filter((item) => item.value && !item.value.includes('n/a'))
        .map((item) => `<p><strong>${item.label}:</strong> ${item.value}</p>`)
        .join('');
}

// Helper function to get cookie value
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return '';
}

// Helper function to set cookie value
function setCookie(name, value, days) {
    const expires = new Date();
    expires.setDate(expires.getDate() + days);
    document.cookie = `${name}=${value}; expires=${expires.toUTCString()}; path=/`;
}

// Save IDs to specific cookie
function saveIdToCookie(cookieName, girlId) {
    let ids = getCookie(cookieName);
    ids = ids ? ids.split(',') : [];

    if (!ids.includes(String(girlId))) {
        ids.push(girlId);
        setCookie(cookieName, ids.join(','), 7); // Save for 7 days
    }
}

// Save girl's ID and name to the cookie
function saveGirlToCookie(girlId, girlName) {
    let likedGirls = getCookie('likedGirls');
    likedGirls = likedGirls ? JSON.parse(likedGirls) : [];

    // Add the new liked girl
    if (!likedGirls.some(girl => girl.id === girlId)) {
        likedGirls.push({id: girlId, name: girlName});
        setCookie('likedGirls', JSON.stringify(likedGirls), 7); // Store for 7 days
    }
}

// Retrieve liked girls from the cookie
function getLikedGirlsFromCookie() {
    const likedGirls = getCookie('likedGirls');
    return likedGirls ? JSON.parse(likedGirls) : [];
}

function showIndexCard() {
    document.getElementById('favorite-card').style.display = 'none';
    document.getElementById('detail-card').style.display = 'none';
    document.getElementById('index-card').style.display = 'block';

    // Load a random girl
    // fetchRandomGirl();
}

function showFavoriteCard() {
    document.getElementById('index-card').style.display = 'none';
    document.getElementById('detail-card').style.display = 'none';
    document.getElementById('favorite-card').style.display = 'block';

    // Populate the liked girls list
    const likedGirls = getLikedGirlsFromCookie();
    const likedGirlsList = document.getElementById('liked-girls-list');
    likedGirlsList.innerHTML = ''; // Clear current list

    likedGirls.forEach(girl => {
        const girlElement = document.createElement('div');
        girlElement.classList.add('liked-girl');
        girlElement.innerHTML = `
            <img src="/static/images/models/${girl.id}.jpg" alt="${girl.name}" class="avatar">
            <span>${girl.name}</span>
        `;
        girlElement.addEventListener('click', () => showDetailCard(girl.id));
        likedGirlsList.appendChild(girlElement);
    });
}

function showDetailCard(girlId) {
    document.getElementById('index-card').style.display = 'none';
    document.getElementById('favorite-card').style.display = 'none';
    document.getElementById('detail-card').style.display = 'block';

    // Fetch girl details based on the selected girl ID
    fetch(`/detail?id=${girlId}`)
        .then(response => response.json())
        .then(data => {
            // Display girl details
            document.getElementById('detail-girl-name').textContent = data.name;
            document.getElementById('google-btn').textContent = 'Google ' + data.name;
            document.getElementById('google-btn').onclick = function () {
                window.open('https://www.google.com/search?q=' + data.name, '_blank');
            };
            document.getElementById('detail-girl-image').innerHTML = `<img src="/static/images/models/${data.id}.jpg" alt="${data.name}" class="consistent-image">`;
            document.getElementById('detail-girl-info').innerHTML = generateFullDetailsHTML(data);
        });
}