document.addEventListener('DOMContentLoaded', function() {
    // Form submission handler
    const desertionForm = document.getElementById('desertionForm');
    desertionForm.addEventListener('submit', function(e) {
        e.preventDefault();
        submitDesertionForm();
    });

    // Load sample data
    document.getElementById('loadSample').addEventListener('click', function() {
        loadSampleData();
    });
});

function submitDesertionForm() {
    // Get form values
    const formData = {
        customer_id: document.getElementById('customer_id').value,
        months_to_maturity: parseInt(document.getElementById('months_to_maturity').value),
        total_relationship_value: parseFloat(document.getElementById('total_relationship_value').value),
        number_of_products: parseInt(document.getElementById('number_of_products').value),
        satisfaction_score: parseFloat(document.getElementById('satisfaction_score').value),
        number_of_complaints: parseInt(document.getElementById('number_of_complaints').value),
        months_since_last_interaction: parseFloat(document.getElementById('months_since_last_interaction').value),
        age: parseInt(document.getElementById('age').value),
        tenure_months: parseInt(document.getElementById('tenure_months').value),
        monthly_average_balance: parseFloat(document.getElementById('monthly_average_balance').value)
    };

    // Show loading spinner
    document.querySelector('button[type="submit"]').innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Đang xử lý...';
    document.querySelector('button[type="submit"]').disabled = true;

    // Send API request (using array of one element for consistency with the API)
    callApi('desertion-strategy/', 'POST', [formData])
        .then(data => {
            displayResults(data);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Đã xảy ra lỗi khi xử lý yêu cầu. Vui lòng thử lại sau.');
        })
        .finally(() => {
            // Reset button
            document.querySelector('button[type="submit"]').innerHTML = 'Phân tích';
            document.querySelector('button[type="submit"]').disabled = false;
        });
}

function displayResults(data) {
    // Show result card, hide about card
    document.getElementById('resultCard').style.display = 'block';
    document.getElementById('aboutCard').style.display = 'none';
    
    // Get strategy data
    const strategies = data.retention_strategies;
    if (!strategies || !strategies.length) {
        alert('Không nhận được kết quả phân tích hợp lệ');
        return;
    }
    
    const strategy = strategies[0]; // We only sent one customer
    
    // Set desertion probability
    const probability = strategy.desertion_probability * 100;
    document.getElementById('desertionProbability').textContent = `${probability.toFixed(1)}%`;
    
    // Set progress bar
    const progressBar = document.getElementById('desertionProgressBar');
    progressBar.style.width = `${probability}%`;
    if (probability < 30) {
        progressBar.className = 'progress-bar bg-success';
    } else if (probability < 70) {
        progressBar.className = 'progress-bar bg-warning';
    } else {
        progressBar.className = 'progress-bar bg-danger';
    }
    
    // Set risk level
    const riskLevel = document.getElementById('riskLevel');
    riskLevel.textContent = strategy.risk_level;
    if (strategy.risk_level === 'Thấp') {
        riskLevel.className = 'badge rounded-pill bg-success fs-6 p-2 mb-2';
    } else if (strategy.risk_level === 'Trung bình') {
        riskLevel.className = 'badge rounded-pill bg-warning fs-6 p-2 mb-2';
    } else if (strategy.risk_level === 'Cao') {
        riskLevel.className = 'badge rounded-pill bg-danger fs-6 p-2 mb-2';
    } else {
        riskLevel.className = 'badge rounded-pill bg-dark fs-6 p-2 mb-2';
    }
    
    // Set primary reason
    document.getElementById('primaryReason').textContent = `Nguyên nhân chính: ${strategy.primary_churn_reason || 'Không xác định'}`;
    
    // Set retention strategy
    document.getElementById('retentionStrategy').textContent = strategy.retention_strategy || 'Không có chiến lược được đề xuất';
    
    // Clear and set action plan
    const actionPlan = document.getElementById('actionPlan');
    actionPlan.innerHTML = '';
    
    // If action_plan exists in the response
    if (strategy.action_plan) {
        actionPlan.innerHTML = `<li class="list-group-item">${strategy.action_plan}</li>`;
    }
    // If not, provide some generic actions based on the data
    else {
        if (strategy.primary_churn_reason === 'Kỳ hạn') {
            addActionItem('Liên hệ trước 2 tháng hết hạn với ưu đãi gia hạn');
        }
        if (strategy.primary_churn_reason === 'Dịch vụ' || strategy.satisfaction_score < 7) {
            addActionItem('Gọi điện khảo sát sự hài lòng và xác định vấn đề');
        }
        if (strategy.months_since_last_interaction > 2) {
            addActionItem('Khởi tạo chiến dịch tiếp cận khách hàng không hoạt động');
        }
        if (strategy.number_of_products < 2) {
            addActionItem('Đề xuất sản phẩm bổ sung với ưu đãi 15% phí/lãi suất');
        }
    }
    
    // Set cost and ROI
    document.getElementById('retentionCost').textContent = formatCurrency(strategy.retention_cost || 0);
    
    const roi = strategy.retention_roi || 0;
    const roiElement = document.getElementById('retentionROI');
    roiElement.textContent = `${(roi * 100).toFixed(1)}%`;
    if (roi > 0.5) {
        roiElement.className = 'mb-0 fs-5 text-success';
    } else if (roi > 0) {
        roiElement.className = 'mb-0 fs-5 text-warning';
    } else {
        roiElement.className = 'mb-0 fs-5 text-danger';
    }
    
    function addActionItem(text) {
        const li = document.createElement('li');
        li.className = 'list-group-item';
        li.textContent = text;
        actionPlan.appendChild(li);
    }
}

function loadSampleData() {
    // Load sample data
    document.getElementById('customer_id').value = 'CUS000321';
    document.getElementById('months_to_maturity').value = '3';
    document.getElementById('total_relationship_value').value = '75000000';
    document.getElementById('number_of_products').value = '2';
    document.getElementById('satisfaction_score').value = '6.5';
    document.getElementById('number_of_complaints').value = '1';
    document.getElementById('months_since_last_interaction').value = '2';
    document.getElementById('age').value = '42';
    document.getElementById('tenure_months').value = '36';
    document.getElementById('monthly_average_balance').value = '8500000';
}

function formatCurrency(value) {
    return new Intl.NumberFormat('vi-VN', { 
        style: 'currency', 
        currency: 'VND',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}
