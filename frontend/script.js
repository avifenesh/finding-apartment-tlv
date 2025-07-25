// Check authentication
const authToken = localStorage.getItem('authToken');
const authTime = localStorage.getItem('authTime');
// Check if authenticated within last 24 hours
if (!authToken || !authTime || (Date.now() - parseInt(authTime) > 86400000)) {
    window.location.href = './login.html';
}

// API base URL - Update this to your backend URL
const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api'
    : 'http://34.247.214.104:8000/api'; // AWS EC2 backend

// State
let apartments = [];
let neighborhoods = [];
let isScrapingInProgress = false;

// Get auth headers
function getAuthHeaders() {
    const token = localStorage.getItem('authToken');
    if (!token) {
        window.location.href = './login.html';
        return {};
    }
    return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };
}

// Initialize app
document.addEventListener('DOMContentLoaded', async () => {
    await loadNeighborhoods();
    await loadStats();
    await loadApartments();
    
    // Set up event listeners
    document.getElementById('scrapeBtn').addEventListener('click', triggerScrape);
    document.getElementById('neighborhoodFilter').addEventListener('change', loadApartments);
    document.getElementById('priceFilter').addEventListener('change', loadApartments);
    document.getElementById('roomsFilter').addEventListener('change', loadApartments);
    
    // Auto-refresh every 30 seconds
    setInterval(async () => {
        await loadStats();
        if (!isScrapingInProgress) {
            await loadApartments();
        }
    }, 30000);
});

// Load neighborhoods
async function loadNeighborhoods() {
    try {
        const response = await fetch(`${API_URL}/neighborhoods`, {
            headers: getAuthHeaders()
        });
        neighborhoods = await response.json();
        
        const select = document.getElementById('neighborhoodFilter');
        neighborhoods.forEach(n => {
            const option = document.createElement('option');
            option.value = n.id;
            option.textContent = n.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading neighborhoods:', error);
    }
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/stats`, {
            headers: getAuthHeaders()
        });
        const stats = await response.json();
        
        document.getElementById('activeCount').textContent = stats.active_apartments;
        document.getElementById('recentCount').textContent = stats.apartments_last_3_days;
        
        if (stats.last_scrape) {
            const date = new Date(stats.last_scrape);
            const timeAgo = getTimeAgo(date);
            document.getElementById('lastScrape').textContent = timeAgo;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load apartments
async function loadApartments() {
    const loading = document.getElementById('loading');
    const grid = document.getElementById('apartmentsGrid');
    const noResults = document.getElementById('noResults');
    
    loading.classList.remove('hidden');
    grid.innerHTML = '';
    noResults.classList.add('hidden');
    
    try {
        // Build query parameters
        const params = new URLSearchParams();
        
        const neighborhood = document.getElementById('neighborhoodFilter').value;
        if (neighborhood) params.append('neighborhood_id', neighborhood);
        
        const maxPrice = document.getElementById('priceFilter').value;
        if (maxPrice) params.append('max_price', maxPrice);
        
        const rooms = document.getElementById('roomsFilter').value;
        if (rooms) {
            params.append('min_rooms', rooms);
            params.append('max_rooms', rooms);
        }
        
        const response = await fetch(`${API_URL}/apartments?${params}`, {
            headers: getAuthHeaders()
        });
        apartments = await response.json();
        
        if (apartments.length === 0) {
            noResults.classList.remove('hidden');
        } else {
            apartments.forEach(apt => {
                grid.appendChild(createApartmentCard(apt));
            });
        }
    } catch (error) {
        console.error('Error loading apartments:', error);
        grid.innerHTML = '<p class="text-center text-red-500">שגיאה בטעינת הדירות</p>';
    } finally {
        loading.classList.add('hidden');
    }
}

// Create apartment card
function createApartmentCard(apartment) {
    const card = document.createElement('div');
    card.className = 'apartment-card bg-white rounded-lg shadow-md overflow-hidden';
    
    const isNew = isNewListing(apartment.publish_date);
    
    card.innerHTML = `
        <div class="relative">
            ${isNew ? '<div class="new-badge">חדש!</div>' : ''}
            <div class="image-carousel" id="carousel-${apartment.id}">
                ${apartment.images.length > 0 
                    ? `<img src="${apartment.images[0]}" alt="${apartment.title}" onclick="showImage('${apartment.images[0]}')">`
                    : '<div class="skeleton w-full h-full"></div>'
                }
                ${apartment.images.length > 1 ? `
                    <button class="carousel-btn prev" onclick="changeImage(${apartment.id}, -1)">❮</button>
                    <button class="carousel-btn next" onclick="changeImage(${apartment.id}, 1)">❯</button>
                ` : ''}
            </div>
        </div>
        <div class="p-4">
            <h3 class="font-bold text-lg mb-2">${apartment.title}</h3>
            <div class="price-tag mb-3">₪${apartment.price.toLocaleString()}</div>
            <div class="space-y-1 text-sm text-gray-600 mb-4">
                <p>🏠 ${apartment.rooms} חדרים</p>
                <p>📍 ${apartment.neighborhood}, ${apartment.address}</p>
                ${apartment.floor ? `<p>🏢 ${apartment.floor}</p>` : ''}
                ${apartment.square_meters ? `<p>📐 ${apartment.square_meters} מ"ר</p>` : ''}
                <p>📅 ${getTimeAgo(new Date(apartment.publish_date))}</p>
            </div>
            <a href="${apartment.link}" target="_blank" class="block w-full text-center bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                צפה במודעה ב-Yad2
            </a>
        </div>
    `;
    
    // Store images data for carousel
    card.dataset.images = JSON.stringify(apartment.images);
    card.dataset.currentIndex = '0';
    
    return card;
}

// Change image in carousel
function changeImage(apartmentId, direction) {
    const carousel = document.getElementById(`carousel-${apartmentId}`);
    const card = carousel.closest('.apartment-card');
    const images = JSON.parse(card.dataset.images);
    let currentIndex = parseInt(card.dataset.currentIndex);
    
    currentIndex += direction;
    if (currentIndex < 0) currentIndex = images.length - 1;
    if (currentIndex >= images.length) currentIndex = 0;
    
    card.dataset.currentIndex = currentIndex;
    const img = carousel.querySelector('img');
    img.src = images[currentIndex];
}

// Show image in modal
function showImage(src) {
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImage');
    modalImg.src = src;
    modal.classList.remove('hidden');
}

// Close modal
function closeModal() {
    document.getElementById('imageModal').classList.add('hidden');
}

// Close modal on click outside
document.getElementById('imageModal').addEventListener('click', (e) => {
    if (e.target.id === 'imageModal') {
        closeModal();
    }
});

// Trigger scrape
async function triggerScrape() {
    const btn = document.getElementById('scrapeBtn');
    
    // Check if already scraping
    const statusResponse = await fetch(`${API_URL}/scrape/status`, {
        headers: getAuthHeaders()
    });
    const status = await statusResponse.json();
    
    if (status.is_scraping) {
        alert('סריקה כבר בתהליך, אנא המתן...');
        return;
    }
    
    btn.disabled = true;
    btn.textContent = 'סורק...';
    isScrapingInProgress = true;
    
    try {
        const response = await fetch(`${API_URL}/scrape`, { 
            method: 'POST',
            headers: getAuthHeaders()
        });
        const result = await response.json();
        
        if (result.success) {
            // Check scraping status periodically
            const checkStatus = setInterval(async () => {
                const statusResponse = await fetch(`${API_URL}/scrape/status`, {
        headers: getAuthHeaders()
    });
                const status = await statusResponse.json();
                
                if (!status.is_scraping) {
                    clearInterval(checkStatus);
                    btn.disabled = false;
                    btn.textContent = 'הפעל סריקה';
                    isScrapingInProgress = false;
                    
                    // Reload data
                    await loadStats();
                    await loadApartments();
                    
                    alert('הסריקה הושלמה בהצלחה!');
                }
            }, 2000);
        } else {
            alert('שגיאה: ' + result.message);
            btn.disabled = false;
            btn.textContent = 'הפעל סריקה';
            isScrapingInProgress = false;
        }
    } catch (error) {
        console.error('Error triggering scrape:', error);
        alert('שגיאה בהפעלת הסריקה');
        btn.disabled = false;
        btn.textContent = 'הפעל סריקה';
        isScrapingInProgress = false;
    }
}

// Helper function to get time ago string
function getTimeAgo(date) {
    const now = new Date();
    const diff = now - date;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(hours / 24);
    
    if (days > 0) {
        return `לפני ${days} ${days === 1 ? 'יום' : 'ימים'}`;
    } else if (hours > 0) {
        return `לפני ${hours} ${hours === 1 ? 'שעה' : 'שעות'}`;
    } else {
        const minutes = Math.floor(diff / (1000 * 60));
        return `לפני ${minutes} ${minutes === 1 ? 'דקה' : 'דקות'}`;
    }
}

// Check if listing is new (within last 24 hours)
function isNewListing(publishDate) {
    const date = new Date(publishDate);
    const now = new Date();
    const diff = now - date;
    const hours = diff / (1000 * 60 * 60);
    return hours <= 24;
}

// Logout function
function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('authTime');
    window.location.href = './login.html';
}