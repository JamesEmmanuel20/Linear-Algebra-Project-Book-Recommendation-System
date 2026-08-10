let chartInstance = null;

document.addEventListener("DOMContentLoaded", () => {
    loadUsers();
    loadAnalyticsChart();
});

// Load user list into dropdown
async function loadUsers() {
    try {
        const response = await fetch('/api/users');
        const data = await response.json();
        const select = document.getElementById('userSelect');
        select.innerHTML = '';
        
        data.users.forEach(user => {
            const opt = document.createElement('option');
            opt.value = user;
            opt.innerText = user;
            select.appendChild(opt);
        });
    } catch (error) {
        console.error("Failed to load users:", error);
    }
}

// Trigger linear algebra engine calculation via API
async function getRecommendations() {
    const user = document.getElementById('userSelect').value;
    const metric = document.getElementById('metricSelect').value;

    try {
        const response = await fetch('/api/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user: user, metric: metric })
        });

        const data = await response.json();
        renderResults(data);
    } catch (error) {
        console.error("Error fetching recommendations:", error);
    }
}

// Display results in UI
function renderResults(data) {
    const resultsCard = document.getElementById('resultsCard');
    const infoDiv = document.getElementById('similarityInfo');
    const list = document.getElementById('recommendationsList');

    resultsCard.classList.remove('hidden');

    const metricLabel = data.metric_used === 'euclidean' 
        ? 'Euclidean Distance ($||\\vec{u} - \\vec{v}||_2$)' 
        : 'Cosine Similarity ($\\cos \\theta$)';

    infoDiv.innerHTML = `
        <p><strong>Target Vector ($\vec{u}$):</strong> ${data.target_user}</p>
        <p><strong>Nearest Neighbor ($\vec{v}$):</strong> ${data.most_similar_user}</p>
        <p><strong>${metricLabel}:</strong> <span class="badge">${data.score}</span></p>
    `;

    list.innerHTML = '';
    if (data.recommendations.length === 0) {
        list.innerHTML = '<li>No items meet the recommendation threshold criteria.</li>';
    } else {
        data.recommendations.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>${item.book.replace(/_/g, ' ')}</strong> — Rated <span>${item.similar_user_rating}/5</span> by ${data.most_similar_user}`;
            list.appendChild(li);
        });
    }
}

// Render Item Mean Vector Bar Chart
async function loadAnalyticsChart() {
    try {
        const response = await fetch('/api/analytics');
        const data = await response.json();

        const ctx = document.getElementById('averageChart').getContext('2d');
        if (chartInstance) chartInstance.destroy();

        chartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.books.map(b => b.replace(/_/g, ' ')),
                datasets: [{
                    label: 'Mean Book Vector Score',
                    data: data.average_ratings,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, max: 5, title: { display: true, text: 'Average Score (1-5)' } },
                    x: { ticks: { maxRotation: 45, minRotation: 45 } }
                }
            }
        });
    } catch (error) {
        console.error("Error loading analytics:", error);
    }
}