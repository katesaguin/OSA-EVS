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
    new Chart(barCtx, {
        type: 'bar',
        data: {
            labels: [
                'Forgotten or misplaced', 'ID not claimed on time',
                'Lack of Awareness of Specific Policy', 'Unforeseen Circumstances',
                'Misinterpretation of dress code compliance', 'Substitution of footwear',
                'Unawareness of mandated garment length requirements', 'Oversight in compliance',
                'Personal style preference conflicting', 'Others'
            ],
            datasets: [{
                data: [21, 2, 152, 79, 166, 39, 179, 141, 55, 12],
                backgroundColor: [
                    '#E74C3C', '#F39C12',
                    '#F7D358', '#A9DFBF',
                    '#229954', '#34495E',
                    '#5DADE2', '#A569BD',
                    '#F5B7B1', '#B2BABB'
                ],
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
