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

    // ——— Element refs ———
  const fromInput = document.getElementById('from_date');
  const toInput   = document.getElementById('to_date');
  const aySelect  = document.getElementById('academic_list');
  const filterForm = document.querySelector('.search-form');

  // ——— Bar chart setup ———
  const barCtx = document.getElementById('remarksBarChart').getContext('2d');
  let barChartInstance = null;

  // Function to (re)load bar chart with optional filters
  function loadBarChart() {
    // Build query string from current filter values
    const params = new URLSearchParams();
    if (fromInput.value) params.append('from_date', fromInput.value);
    if (toInput.value)   params.append('to_date',   toInput.value);
    if (aySelect.value)  params.append('academic_list', aySelect.value);

    fetch('/xu-entry-violation/get-reasons?' + params.toString())
      .then(res => {
        if (!res.ok) throw new Error('Network response was not ok');
        return res.json();
      })
      .then(data => {
        const counts = data.reason_counts;
        const labels = counts.map(o => o.reason_text);
        const values = counts.map(o => o.count);
        const colors = counts.map(o => o.color || '#000000');

        // destroy old chart if it exists
        if (barChartInstance) barChartInstance.destroy();

        barChartInstance = new Chart(barCtx, {
          type: 'bar',
          data: {
            labels: labels,
            datasets: [{
              data: values,
              backgroundColor: colors,
              borderWidth: 0
            }]
          },
          options: {
            plugins: { legend: { display: false } },
            scales: {
              x: { display: false },
              y: {
                beginAtZero: true,
                ticks: { stepSize: 50 }
              }
            }
          }
        });
      })
      .catch(err => console.error('Error fetching reason counts:', err));
  }

  // Initial load
  loadBarChart();
});