document.addEventListener('DOMContentLoaded', function() {
    // Form submission handler
    const applicationForm = document.getElementById('applicationForm');
    applicationForm.addEventListener('submit', function(e) {
        e.preventDefault();
        submitApplicationForm();
    });

    // Load sample data
    document.getElementById('loadSample').addEventListener('click', function() {
        loadSampleData();
    });
});

function submitApplicationForm() {
    // Get form values
    const formData = {
        customer_id: document.getElementById('customer_id').value,
        age: parseInt(document.getElementById('age').value),
        income: parseFloat(document.getElementById('income').value),
        employment_length: parseFloat(document.getElementById('employment_length').value),
        debt_to_income: parseFloat(document.getElementById('debt_to_income').value),
        credit_history_length: parseFloat(document.getElementById('credit_history_length').value),
        number_of_debts: parseInt(document.getElementById('number_of_debts').value),
        number_of_delinquent_debts: parseInt(document.getElementById('number_of_delinquent_debts').value),
        homeowner: parseInt(document.getElementById('homeowner').value)
    };

    // Show loading spinner
    document.querySelector('button[type="submit"]').innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Đang xử lý...';
    document.querySelector('button[type="submit"]').disabled = true;

    // Send API request
    callApi('application-score/', 'POST', formData)
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
    
    const riskProfile = data.risk_profile;
    
    // Set credit score
    const creditScore = riskProfile.credit_score || 0;
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
    
    // Set risk level badge
    const riskLevel = document.getElementById('riskLevel');
    riskLevel.textContent = riskProfile.risk_level || 'N/A';
    if (riskProfile.risk_level === 'Low') {
        riskLevel.className = 'badge rounded-pill bg-success';
    } else if (riskProfile.risk_level === 'Medium') {
        riskLevel.className = 'badge rounded-pill bg-warning';
    } else {
        riskLevel.className = 'badge rounded-pill bg-danger';
    }
    
    // Set default probability
    const defaultProb = riskProfile.default_probability || 0;
    document.getElementById('defaultProbability').textContent = `${(defaultProb * 100).toFixed(2)}%`;
    
    // Set suggested action badge
    const suggestedAction = document.getElementById('suggestedAction');
    suggestedAction.textContent = riskProfile.suggested_action || 'N/A';
    if (riskProfile.suggested_action === 'Approve') {
        suggestedAction.className = 'badge rounded-pill bg-success';
    } else if (riskProfile.suggested_action === 'Review') {
        suggestedAction.className = 'badge rounded-pill bg-warning';
    } else {
        suggestedAction.className = 'badge rounded-pill bg-danger';
    }
    
    // Set risk factors
    const riskFactorsList = document.getElementById('riskFactorsList');
    riskFactorsList.innerHTML = '';
    
    // If top_risk_factors exists in the response
    if (riskProfile.top_risk_factors && Array.isArray(riskProfile.top_risk_factors)) {
        riskProfile.top_risk_factors.forEach(factor => {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.textContent = factor;
            riskFactorsList.appendChild(li);
        });
    } else {
        // Create some generic risk factors based on the input data
        const formData = {
            age: parseInt(document.getElementById('age').value),
            income: parseFloat(document.getElementById('income').value),
            debt_to_income: parseFloat(document.getElementById('debt_to_income').value),
            credit_history_length: parseFloat(document.getElementById('credit_history_length').value),
            number_of_delinquent_debts: parseInt(document.getElementById('number_of_delinquent_debts').value),
        };
        
        if (formData.age < 25) {
            addRiskFactor('Tuổi khách hàng thấp');
        }
        if (formData.debt_to_income > 0.4) {
            addRiskFactor('Tỷ lệ nợ/thu nhập cao');
        }
        if (formData.credit_history_length < 2) {
            addRiskFactor('Lịch sử tín dụng ngắn');
        }
        if (formData.number_of_delinquent_debts > 0) {
            addRiskFactor('Có khoản nợ quá hạn');
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
    document.getElementById('customer_id').value = 'CUS000123';
    document.getElementById('age').value = '35';
    document.getElementById('income').value = '50000';
    document.getElementById('employment_length').value = '5.5';
    document.getElementById('debt_to_income').value = '0.25';
    document.getElementById('credit_history_length').value = '7';
    document.getElementById('number_of_debts').value = '2';
    document.getElementById('number_of_delinquent_debts').value = '0';
    document.getElementById('homeowner').value = '1';
}
