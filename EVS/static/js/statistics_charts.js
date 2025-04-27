// statistics_charts.js
// Placeholder data for demonstration. REPLACEEE THE DATA HERE!
document.addEventListener('DOMContentLoaded', function () {
    // Donut Chart (Violation Distribution)
    const donutCtx = document.getElementById('violationDonutChart').getContext('2d');
    new Chart(donutCtx, {
        type: 'doughnut',
        data: {
            labels: ['Uniform Violation', 'Dress Code Violation', 'ID Violation'],
            datasets: [{
                data: typeof donutData !== 'undefined' ? donutData : [0, 0, 0],
                backgroundColor: ['#2E5AAC', '#69A8F7', '#19387E'],
                borderWidth: 0
            }]
        },
        options: {
            plugins: {
                legend: {
                    display: false
                }
            },
            cutout: '70%'
        }
    });

    // Bar Chart (Common Trends)
    const barCtx = document.getElementById('remarksBarChart').getContext('2d');
    // Get dynamic reasons from localStorage, fallback to defaults
    const defaultReasons = [
      {reason: 'Forgotten or misplaced', color: '#E74C3C'},
      {reason: 'ID not claimed on time', color: '#F39C12'},
      {reason: 'Lack of Awareness of Specific Policy', color: '#F7D358'},
      {reason: 'Unforeseen Circumstances', color: '#A9DFBF'},
      {reason: 'Misinterpretation of dress code compliance', color: '#229954'},
      {reason: 'Substitution of footwear', color: '#34495E'},
      {reason: 'Unawareness of mandated garment length requirements', color: '#5DADE2'},
      {reason: 'Oversight in compliance', color: '#A569BD'},
      {reason: 'Personal style preference conflicting', color: '#F5B7B1'},
      {reason: 'Others', color: '#B2BABB'}
    ];
    let reasons = [];
    try {
      reasons = JSON.parse(localStorage.getItem('reasons')) || defaultReasons;
    } catch (e) {
      reasons = defaultReasons;
    }
    const reasonLabels = reasons.map(r => r.reason);
    const reasonColors = reasons.map(r => r.color);
    // You may want to fetch data dynamically, for now use dummy data of same length
    const dummyData = Array(reasonLabels.length).fill(0).map((_,i) => (21 + i*5) % 100);
    new Chart(barCtx, {
        type: 'bar',
        data: {
            labels: reasonLabels,
            datasets: [{
                data: dummyData,
                backgroundColor: reasonColors,
                borderWidth: 0
            }]
        },
        options: {
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 50 }
                }
            }
        }
    });
});
