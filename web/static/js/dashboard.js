document.addEventListener('DOMContentLoaded', function() {
    // Check if required Bootstrap objects exist
    if (typeof bootstrap === 'undefined') {
        console.error('Bootstrap JS is not loaded. Charts may not function correctly.');
    }
    
    // Add delay to ensure DOM is fully rendered
    setTimeout(function() {
        try {
            // Initialize date inputs with appropriate values
            initializeDateRange();
            
            // Initialize all charts
            initializeCharts();
            
            // Add event listeners
            document.getElementById('dateRange').addEventListener('change', handleDateRangeChange);
            document.getElementById('refreshData').addEventListener('click', refreshDashboardData);
            document.getElementById('exportDashboard').addEventListener('click', exportDashboardReport);
            
            console.log('Dashboard initialized successfully');
        } catch (error) {
            console.error('Error initializing dashboard:', error);
        }
    }, 100);
});

function initializeDateRange() {
    // Set default date range (last 7 days)
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 7);
    
    document.getElementById('startDate').valueAsDate = startDate;
    document.getElementById('endDate').valueAsDate = endDate;
    
    // Initially disable custom date inputs since dropdown is set to "7 days"
    toggleCustomDateInputs(false);
}

function handleDateRangeChange() {
    const dateRange = document.getElementById('dateRange').value;
    const endDate = new Date();
    let startDate = new Date();
    
    switch(dateRange) {
        case 'today':
            startDate = new Date();
            break;
        case 'yesterday':
            startDate = new Date();
            startDate.setDate(startDate.getDate() - 1);
            endDate.setDate(endDate.getDate() - 1);
            break;
        case '7days':
            startDate.setDate(startDate.getDate() - 7);
            break;
        case '30days':
            startDate.setDate(startDate.getDate() - 30);
            break;
        case '90days':
            startDate.setDate(startDate.getDate() - 90);
            break;
        case 'custom':
            // Enable custom date inputs
            toggleCustomDateInputs(true);
            return;
    }
    
    // Disable custom date inputs for preset ranges
    toggleCustomDateInputs(false);
    
    // Update date inputs
    document.getElementById('startDate').valueAsDate = startDate;
    document.getElementById('endDate').valueAsDate = endDate;
    
    // Refresh dashboard with new date range
    refreshDashboardData();
}

function toggleCustomDateInputs(enabled) {
    document.getElementById('startDate').disabled = !enabled;
    document.getElementById('endDate').disabled = !enabled;
}

function refreshDashboardData() {
    // In a real application, this would fetch updated data from the API
    console.log('Refreshing dashboard data...');
    
    // For demonstration, we'll just reinitialize the charts
    initializeCharts();
    
    // Show a toast notification
    showToast('Dữ liệu đã được cập nhật thành công!');
}

function exportDashboardReport() {
    // In a real application, this would generate a PDF or Excel report
    console.log('Exporting dashboard report...');
    showToast('Báo cáo đang được tạo...', 'info');
    
    // Simulate delay for report generation
    setTimeout(() => {
        showToast('Xuất báo cáo thành công!', 'success');
    }, 2000);
}

function showToast(message, type = 'success') {
    try {
        // Create toast container if it doesn't exist
        if (!document.getElementById('toastContainer')) {
            const container = document.createElement('div');
            container.id = 'toastContainer';
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(container);
        }
        
        // Create toast element
        const toastId = 'toast-' + Date.now();
        const toastHtml = `
            <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header bg-${type} text-white">
                    <strong class="me-auto">Dashboard</strong>
                    <small>Just now</small>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;
        
        // Add toast to container
        document.getElementById('toastContainer').innerHTML += toastHtml;
        
        // Check if Bootstrap is available
        if (typeof bootstrap === 'undefined') {
            console.error('Bootstrap JS not available, cannot show toast notification');
            return;
        }
        
        // Initialize and show the toast
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, {
            delay: 3000
        });
        toast.show();
        
        // Remove toast from DOM after it's hidden
        toastElement.addEventListener('hidden.bs.toast', function () {
            toastElement.remove();
        });
    } catch (error) {
        console.error('Error showing toast notification:', error);
    }
}

function initializeCharts() {
    // Check if Chart is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded. Charts cannot be initialized.');
        return;
    }
    
    console.log('Initializing dashboard charts...');
    
    try {
        // Initialize all charts with sample data
        initializeScoreDistributionChart();
        initializeApprovalDecisionsChart();
        initializeDefaultTrendChart();
        initializeCollectionPerformanceChart();
        initializeRiskSegmentsChart();
        
        console.log('All charts initialized successfully');
    } catch (error) {
        console.error('Error initializing charts:', error);
    }
}

function initializeScoreDistributionChart() {
    const chartElement = document.getElementById('scoreDistributionChart');
    if (!chartElement) {
        console.error('Chart element "scoreDistributionChart" not found');
        return;
    }
    
    const ctx = chartElement.getContext('2d');
    
    try {
        // Destroy existing chart if any
        if (window.scoreDistributionChart) {
            window.scoreDistributionChart.destroy();
        }
        
        window.scoreDistributionChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['300-350', '351-400', '401-450', '451-500', '501-550', '551-600', '601-650', '651-700', '701-750', '751-800', '801-850'],
                datasets: [{
                    label: 'Number of Customers',
                    data: [15, 28, 42, 78, 156, 220, 245, 198, 132, 85, 42],
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Customers'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Credit Score Range'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Credit Score Distribution'
                    }
                }
            }
        });
        console.log('Score distribution chart initialized');
    } catch (error) {
        console.error('Error initializing score distribution chart:', error);
    }
}

function initializeApprovalDecisionsChart() {
    const chartElement = document.getElementById('approvalDecisionsChart');
    if (!chartElement) {
        console.error('Chart element "approvalDecisionsChart" not found');
        return;
    }
    
    const ctx = chartElement.getContext('2d');
    
    try {
        // Destroy existing chart if any
        if (window.approvalDecisionsChart) {
            window.approvalDecisionsChart.destroy();
        }
        
        window.approvalDecisionsChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Approve', 'Review', 'Reject'],
                datasets: [{
                    data: [68, 18, 14],
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.7)',
                        'rgba(255, 206, 86, 0.7)',
                        'rgba(255, 99, 132, 0.7)'
                    ],
                    borderColor: [
                        'rgba(75, 192, 192, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(255, 99, 132, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Approval Decisions'
                    }
                }
            }
        });
        console.log('Approval decisions chart initialized');
    } catch (error) {
        console.error('Error initializing approval decisions chart:', error);
    }
}

function initializeDefaultTrendChart() {
    const chartElement = document.getElementById('defaultTrendChart');
    if (!chartElement) {
        console.error('Chart element "defaultTrendChart" not found');
        return;
    }
    
    const ctx = chartElement.getContext('2d');
    
    try {
        // Destroy existing chart if any
        if (window.defaultTrendChart) {
            window.defaultTrendChart.destroy();
        }
        
        window.defaultTrendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['01/05', '02/05', '03/05', '04/05', '05/05', '06/05', '07/05', '08/05', '09/05', '10/05', '11/05', '12/05', '13/05', '14/05', '15/05'],
                datasets: [{
                    label: 'Default Rate (%)',
                    data: [4.8, 4.7, 4.9, 4.7, 4.6, 4.5, 4.4, 4.3, 4.4, 4.2, 4.3, 4.1, 4.2, 4.0, 4.2],
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        suggestedMin: 3,
                        suggestedMax: 6,
                        title: {
                            display: true,
                            text: 'Default Rate (%)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Default Trend'
                    }
                }
            }
        });
        console.log('Default trend chart initialized');
    } catch (error) {
        console.error('Error initializing default trend chart:', error);
    }
}

function initializeCollectionPerformanceChart() {
    const chartElement = document.getElementById('collectionPerformanceChart');
    if (!chartElement) {
        console.error('Chart element "collectionPerformanceChart" not found');
        return;
    }
    
    const ctx = chartElement.getContext('2d');
    
    try {
        // Destroy existing chart if any
        if (window.collectionPerformanceChart) {
            window.collectionPerformanceChart.destroy();
        }
        
        window.collectionPerformanceChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Champion', 'Negotiable', 'Cure', 'Restructure', 'Legal', 'Write-off'],
                datasets: [
                    {
                        label: 'Recovery Rate (%)',
                        data: [92, 78, 65, 45, 28, 12],
                        backgroundColor: 'rgba(75, 192, 192, 0.7)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Number of Accounts',
                        data: [120, 220, 310, 180, 95, 45],
                        backgroundColor: 'rgba(54, 162, 235, 0.7)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1,
                        type: 'line',
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Recovery Rate (%)'
                        },
                        position: 'left'
                    },
                    y1: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Accounts'
                        },
                        position: 'right',
                        grid: {
                            drawOnChartArea: false
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Collection Performance'
                    }
                }
            }
        });
        console.log('Collection performance chart initialized');
    } catch (error) {
        console.error('Error initializing collection performance chart:', error);
    }
}

function initializeRiskSegmentsChart() {
    const chartElement = document.getElementById('riskSegmentsChart');
    if (!chartElement) {
        console.error('Chart element "riskSegmentsChart" not found');
        return;
    }
    
    const ctx = chartElement.getContext('2d');
    
    try {
        // Destroy existing chart if any
        if (window.riskSegmentsChart) {
            window.riskSegmentsChart.destroy();
        }
        
        window.riskSegmentsChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Low Risk', 'Medium Risk', 'High Risk', 'Very High Risk'],
                datasets: [{
                    data: [45, 32, 18, 5],
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.7)',
                        'rgba(255, 206, 86, 0.7)',
                        'rgba(255, 159, 64, 0.7)',
                        'rgba(255, 99, 132, 0.7)'
                    ],
                    borderColor: [
                        'rgba(75, 192, 192, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(255, 159, 64, 1)',
                        'rgba(255, 99, 132, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Risk Segments'
                    }
                }
            }
        });
        console.log('Risk segments chart initialized');
    } catch (error) {
        console.error('Error initializing risk segments chart:', error);
    }
}
