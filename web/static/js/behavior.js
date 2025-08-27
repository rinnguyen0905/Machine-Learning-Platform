document.addEventListener('DOMContentLoaded', function() {
    // Form submission handler
    const behaviorForm = document.getElementById('behaviorForm');
    behaviorForm.addEventListener('submit', function(e) {
        e.preventDefault();
        submitBehaviorForm();
    });

    // Load sample data
    document.getElementById('loadSample').addEventListener('click', function() {
        loadSampleData();
    });
});

function submitBehaviorForm() {
    // Get form values
    const formData = {
        customer_id: document.getElementById('customer_id').value,
        current_balance: parseFloat(document.getElementById('current_balance').value),
        average_monthly_payment: parseFloat(document.getElementById('average_monthly_payment').value),
        payment_ratio: parseFloat(document.getElementById('payment_ratio').value),
        number_of_late_payments: parseInt(document.getElementById('number_of_late_payments').value),
        months_since_last_late_payment: parseInt(document.getElementById('months_since_last_late_payment').value),
        number_of_credit_inquiries: parseInt(document.getElementById('number_of_credit_inquiries').value),
        current_limit: parseFloat(document.getElementById('current_limit').value),
        average_utilization: parseFloat(document.getElementById('average_utilization').value)
    };

    // Show loading spinner
    document.querySelector('button[type="submit"]').innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Đang xử lý...';
    document.querySelector('button[type="submit"]').disabled = true;

    // Send API request
    callApi('behavior-score/', 'POST', formData)
        .then(data => {
            displayResults(data);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Đã xảy ra lỗi khi xử lý yêu cầu. Vui lòng thử lại sau.');
        })
        .finally(() => {
            // Reset button
            document.querySelector('button[type="submit"]').innerHTML = 'Đánh giá';
            document.querySelector('button[type="submit"]').disabled = false;
        });
}

function displayResults(data) {
    // Show result card
    document.getElementById('resultCard').style.display = 'block';
    document.getElementById('aboutCard').style.display = 'none';
    
    const recommendation = data.credit_recommendation;
    
    // Set credit score
    const creditScore = recommendation.credit_score || 0;
    document.getElementById('creditScore').textContent = `Điểm tín dụng: ${creditScore}`;
    
    // Set progress bar
    const scorePercentage = (creditScore - 300) / (850 - 300) * 100;
    const progressBar = document.getElementById('scoreProgressBar');
    progressBar.style.width = `${scorePercentage}%`;
    
    // Set color based on score
    if (creditScore >= 750) {
        progressBar.className = 'progress-bar bg-success';
    } else if (creditScore >= 700) {
        progressBar.className = 'progress-bar bg-info';
    } else if (creditScore >= 650) {
        progressBar.className = 'progress-bar bg-warning';
    } else {
        progressBar.className = 'progress-bar bg-danger';
    }
    
    // Set limit values
    const currentLimit = parseFloat(document.getElementById('current_limit').value);
    document.getElementById('currentLimit').textContent = formatCurrency(currentLimit);
    
    const suggestedLimit = recommendation.suggested_limit || 0;
    document.getElementById('suggestedLimit').textContent = formatCurrency(suggestedLimit);
    
    // Calculate and display limit change
    const limitChange = suggestedLimit - currentLimit;
    const limitChangeElement = document.getElementById('limitChange');
    if (limitChange > 0) {
        limitChangeElement.textContent = `+${formatCurrency(limitChange)} (+${((limitChange/currentLimit)*100).toFixed(1)}%)`;
        limitChangeElement.className = 'text-success fw-bold';
    } else if (limitChange < 0) {
        limitChangeElement.textContent = `${formatCurrency(limitChange)} (${((limitChange/currentLimit)*100).toFixed(1)}%)`;
        limitChangeElement.className = 'text-danger fw-bold';
    } else {
        limitChangeElement.textContent = 'Không thay đổi';
        limitChangeElement.className = 'text-secondary';
    }
    
    // Set risk level badge
    const riskLevel = document.getElementById('riskLevel');
    riskLevel.textContent = recommendation.risk_level || 'N/A';
    if (recommendation.risk_level === 'Low') {
        riskLevel.className = 'badge rounded-pill bg-success';
    } else if (recommendation.risk_level === 'Medium') {
        riskLevel.className = 'badge rounded-pill bg-warning';
    } else {
        riskLevel.className = 'badge rounded-pill bg-danger';
    }
    
    // Set default probability
    const defaultProb = recommendation.default_probability || 0;
    document.getElementById('defaultProbability').textContent = `${(defaultProb * 100).toFixed(2)}%`;
    
    // Set suggested action badge
    const suggestedAction = document.getElementById('suggestedAction');
    suggestedAction.textContent = recommendation.suggested_action || 'N/A';
    if (recommendation.suggested_action === 'Increase') {
        suggestedAction.className = 'badge rounded-pill bg-success';
        suggestedAction.textContent = 'Tăng hạn mức';
    } else if (recommendation.suggested_action === 'Maintain') {
        suggestedAction.className = 'badge rounded-pill bg-secondary';
        suggestedAction.textContent = 'Giữ nguyên';
    } else {
        suggestedAction.className = 'badge rounded-pill bg-danger';
        suggestedAction.textContent = 'Giảm hạn mức';
    }
    
    // Set risk factors
    const riskFactorsList = document.getElementById('riskFactorsList');
    riskFactorsList.innerHTML = '';
    
    // If top_risk_factors exists in the response
    if (recommendation.top_risk_factors && Array.isArray(recommendation.top_risk_factors)) {
        recommendation.top_risk_factors.forEach(factor => {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.textContent = factor;
            riskFactorsList.appendChild(li);
        });
    } else {
        // Create some generic risk factors based on the input data
        const formData = {
            payment_ratio: parseFloat(document.getElementById('payment_ratio').value),
            number_of_late_payments: parseInt(document.getElementById('number_of_late_payments').value),
            months_since_last_late_payment: parseInt(document.getElementById('months_since_last_late_payment').value),
            average_utilization: parseFloat(document.getElementById('average_utilization').value)
        };
        
        if (formData.payment_ratio < 0.5) {
            addRiskFactor('Tỷ lệ thanh toán thấp');
        }
        if (formData.number_of_late_payments > 1) {
            addRiskFactor('Nhiều lần thanh toán trễ');
        }
        if (formData.months_since_last_late_payment < 6 && formData.number_of_late_payments > 0) {
            addRiskFactor('Thanh toán trễ gần đây');
        }
        if (formData.average_utilization > 0.7) {
            addRiskFactor('Mức sử dụng tín dụng cao');
        }
    }
    
    function addRiskFactor(text) {
        const li = document.createElement('li');
        li.className = 'list-group-item';
        li.textContent = text;
        riskFactorsList.appendChild(li);
    }
}

function loadSampleData() {
    // Load sample data
    document.getElementById('customer_id').value = 'CUS000456';
    document.getElementById('current_balance').value = '3500';
    document.getElementById('average_monthly_payment').value = '850';
    document.getElementById('payment_ratio').value = '0.65';
    document.getElementById('number_of_late_payments').value = '1';
    document.getElementById('months_since_last_late_payment').value = '8';
    document.getElementById('number_of_credit_inquiries').value = '2';
    document.getElementById('current_limit').value = '10000';
    document.getElementById('average_utilization').value = '0.35';
}

function formatCurrency(value) {
    return new Intl.NumberFormat('vi-VN', { 
        style: 'currency', 
        currency: 'VND',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}
