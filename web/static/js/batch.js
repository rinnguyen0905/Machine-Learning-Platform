// ...existing code...

// Update this function to connect the template download button for manual input
document.addEventListener('DOMContentLoaded', function() {
    // ...existing code...
    
    // Download template button for file upload
    document.getElementById('downloadTemplate').addEventListener('click', function() {
        downloadTemplate('file');
    });
    
    // Add new button for manual input sample
    // First ensure the button exists in the HTML
    if (!document.getElementById('downloadManualTemplate')) {
        const manualInputForm = document.getElementById('manualInputForm');
        const submitButton = manualInputForm.querySelector('button[type="submit"]');
        const templateButton = document.createElement('button');
        templateButton.type = 'button';
        templateButton.className = 'btn btn-outline-secondary me-2';
        templateButton.id = 'downloadManualTemplate';
        templateButton.textContent = 'Tải mẫu';
        
        // Insert before the submit button
        submitButton.parentNode.insertBefore(templateButton, submitButton);
    }
    
    // Add event listener for the new button
    document.getElementById('downloadManualTemplate').addEventListener('click', function() {
        downloadManualTemplate();
    });
    
    // Add form submission handlers
    document.getElementById('fileUploadForm').addEventListener('submit', function(e) {
        e.preventDefault();
        handleFileUpload();
    });
    
    document.getElementById('manualInputForm').addEventListener('submit', function(e) {
        e.preventDefault();
        handleManualInput();
    });
    
    // Add export results handler
    document.getElementById('exportResults').addEventListener('click', function() {
        exportResults();
    });
    
    // ...existing code...
});

// Add a new function to handle manual template downloads
function downloadManualTemplate() {
    const modelType = document.getElementById('manualModelType').value;
    
    if (!modelType) {
        alert('Vui lòng chọn loại mô hình trước khi tải mẫu');
        return;
    }
    
    // Generate sample data based on model type
    let sampleIds;
    
    switch(modelType) {
        case 'application':
            sampleIds = "CUS000123\nCUS000124\nCUS000125\nCUS000126\nCUS000127";
            break;
        case 'behavior':
            sampleIds = "CUS000456\nCUS000457\nCUS000458\nCUS000459\nCUS000460";
            break;
        case 'collections':
            sampleIds = "CUS000789\nCUS000790\nCUS000791\nCUS000792\nCUS000793";
            break;
        case 'desertion':
            sampleIds = "CUS000321\nCUS000322\nCUS000323\nCUS000324\nCUS000325";
            break;
        default:
            sampleIds = "CUS000001\nCUS000002\nCUS000003\nCUS000004\nCUS000005";
    }
    
    // Populate the textarea with the sample data
    document.getElementById('customerIDs').value = sampleIds;
    
    // Show a message to the user
    alert('Mẫu ID khách hàng đã được tải. Bạn có thể chỉnh sửa danh sách này trước khi xử lý.');
}

// Enhance the existing downloadTemplate function to handle both file and manual templates
function downloadTemplate(type = 'file') {
    const modelTypeElement = type === 'file' ? 
        document.getElementById('fileModelType') : 
        document.getElementById('manualModelType');
    
    const modelType = modelTypeElement.value;
    
    if (!modelType) {
        alert('Vui lòng chọn loại mô hình trước khi tải mẫu');
        return;
    }
    
    // Generate CSV content based on model type
    let csvContent = "";
    let filename = "";
    
    switch(modelType) {
        case 'application':
            csvContent = "customer_id,age,income,employment_length,debt_to_income,credit_history_length,number_of_debts,number_of_delinquent_debts,homeowner\n";
            csvContent += "CUS000123,35,50000,5.5,0.25,7,2,0,1\n";
            csvContent += "CUS000124,42,60000,8.0,0.15,12,1,0,1\n";
            csvContent += "CUS000125,29,35000,3.0,0.35,4,3,1,0\n";
            filename = "application_template.csv";
            break;
        case 'behavior':
            csvContent = "customer_id,current_balance,average_monthly_payment,payment_ratio,number_of_late_payments,months_since_last_late_payment,number_of_credit_inquiries,current_limit,average_utilization\n";
            csvContent += "CUS000456,3500,850,0.65,1,8,2,10000,0.35\n";
            csvContent += "CUS000457,4500,950,0.7,0,12,1,12000,0.38\n";
            csvContent += "CUS000458,2800,600,0.55,2,3,3,8000,0.42\n";
            filename = "behavior_template.csv";
            break;
        case 'collections':
            csvContent = "customer_id,days_past_due,outstanding_amount,number_of_contacts,previous_late_payments,promised_payment_amount,broken_promises,months_on_book,last_payment_amount\n";
            csvContent += "CUS000789,45,2500,3,2,500,1,24,300\n";
            csvContent += "CUS000790,60,3600,5,3,1000,2,18,450\n";
            csvContent += "CUS000791,75,3200,4,3,800,2,30,350\n";
            filename = "collections_template.csv";
            break;
        case 'desertion':
            csvContent = "customer_id,months_to_maturity,total_relationship_value,number_of_products,satisfaction_score,number_of_complaints,months_since_last_interaction,age,tenure_months,monthly_average_balance\n";
            csvContent += "CUS000321,3,75000,2,6.5,1,2,42,36,8500\n";
            csvContent += "CUS000322,1,125000,3,8.0,0,0.5,35,60,12000\n";
            csvContent += "CUS000323,2,95000,2,7.5,0,1,38,48,9500\n";
            filename = "desertion_template.csv";
            break;
        default:
            alert('Không tìm thấy mẫu cho loại mô hình này');
            return;
    }
    
    // Create and download the file
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    
    // Create a URL for the blob
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", filename);
    link.style.visibility = 'hidden';
    
    // Append the link to body, click it, then remove it
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Enhance the displayBatchResults function to properly show results
function displayBatchResults(response, modelType) {
    console.log("Displaying batch results:", response, modelType);
    
    // Show results card - make sure this works
    const resultsCard = document.getElementById('resultsCard');
    resultsCard.style.display = 'block';
    
    // Scroll to results
    resultsCard.scrollIntoView({ behavior: 'smooth' });
    
    // Get results array based on model type
    let results = [];
    if (response.results) {
        results = response.results;
    } else if (response.prioritized_accounts) {
        results = response.prioritized_accounts;
    } else if (response.retention_strategies) {
        results = response.retention_strategies;
    } else {
        console.warn("No results found in response:", response);
        
        // Show error message in the results card
        resultsCard.querySelector('.card-body').innerHTML = `
            <div class="alert alert-warning">
                <h5>Không tìm thấy kết quả</h5>
                <p>Không có dữ liệu kết quả được trả về từ API. Vui lòng kiểm tra dữ liệu đầu vào và thử lại.</p>
                <pre class="mt-3">${JSON.stringify(response, null, 2)}</pre>
            </div>
        `;
        return;
    }
    
    if (!results || results.length === 0) {
        // Show error message if no results
        resultsCard.querySelector('.card-body').innerHTML = `
            <div class="alert alert-warning">
                <h5>Không có kết quả</h5>
                <p>Không có khách hàng nào được xử lý thành công. Vui lòng kiểm tra dữ liệu đầu vào và thử lại.</p>
            </div>
        `;
        return;
    }
    
    // Save results for export
    window.batchResults = results;
    window.batchModelType = modelType;
    
    // Set up table headers based on model type
    const tableHead = document.getElementById('resultsTableHead');
    tableHead.innerHTML = '';
    
    const headerRow = document.createElement('tr');
    
    // Common column: Customer ID
    headerRow.innerHTML = '<th>ID khách hàng</th>';
    
    // Model-specific columns
    if (modelType === 'application') {
        headerRow.innerHTML += `
            <th>Điểm tín dụng</th>
            <th>Xác suất vỡ nợ</th>
            <th>Mức độ rủi ro</th>
            <th>Đề xuất</th>
        `;
    } else if (modelType === 'behavior') {
        headerRow.innerHTML += `
            <th>Điểm tín dụng</th>
            <th>Hạn mức hiện tại</th>
            <th>Hạn mức đề xuất</th>
            <th>Thay đổi</th>
            <th>Đề xuất</th>
        `;
    } else if (modelType === 'collections') {
        headerRow.innerHTML += `
            <th>Điểm ưu tiên</th>
            <th>Chiến lược thu hồi</th>
            <th>Số tiền nợ</th>
            <th>Giá trị kỳ vọng</th>
            <th>ROI</th>
        `;
    } else if (modelType === 'desertion') {
        headerRow.innerHTML += `
            <th>Xác suất rời bỏ</th>
            <th>Mức độ rủi ro</th>
            <th>Nguyên nhân</th>
            <th>Chiến lược giữ chân</th>
            <th>Chi phí</th>
        `;
    }
    
    tableHead.appendChild(headerRow);
    
    // Fill table body
    const tableBody = document.getElementById('resultsTableBody');
    tableBody.innerHTML = '';
    
    // Process and display each result
    results.forEach((result, index) => {
        const row = document.createElement('tr');
        
        // Get customer ID
        const customerId = result.customer_id || 'N/A';
        row.innerHTML = `<td>${customerId}</td>`;
        
        // Add model-specific data
        if (modelType === 'application') {
            const profile = result.risk_profile || {};
            row.innerHTML += `
                <td>${profile.credit_score || 'N/A'}</td>
                <td>${profile.default_probability ? (profile.default_probability * 100).toFixed(1) + '%' : 'N/A'}</td>
                <td>${getRiskLevelBadge(profile.risk_level || 'Unknown')}</td>
                <td>${getActionBadge(profile.suggested_action || 'Unknown')}</td>
            `;
        } else if (modelType === 'behavior') {
            const rec = result.credit_recommendation || {};
            const currentLimit = rec.current_limit || 0;
            const suggestedLimit = rec.suggested_limit || 0;
            const limitChange = suggestedLimit - currentLimit;
            const changePercent = currentLimit > 0 ? ((limitChange / currentLimit) * 100).toFixed(1) : '0.0';
            
            const changeText = limitChange >= 0 ? 
                `+${formatCurrency(limitChange)} (+${changePercent}%)` :
                `${formatCurrency(limitChange)} (${changePercent}%)`;
                
            const changeClass = limitChange > 0 ? 'text-success' : (limitChange < 0 ? 'text-danger' : '');
            
            row.innerHTML += `
                <td>${rec.credit_score || 'N/A'}</td>
                <td>${formatCurrency(currentLimit)}</td>
                <td>${formatCurrency(suggestedLimit)}</td>
                <td class="${changeClass} fw-bold">${changeText}</td>
                <td>${getActionBadge(rec.suggested_action || 'Unknown')}</td>
            `;
        } else if (modelType === 'collections') {
            row.innerHTML += `
                <td>${Math.round(result.priority_score || 0)}</td>
                <td>${getCollectionStrategyBadge(result.collection_strategy || 'Unknown')}</td>
                <td>${formatCurrency(result.outstanding_amount || 0)}</td>
                <td>${formatCurrency(result.expected_recovery_value || 0)}</td>
                <td>${(result.recovery_roi || 0).toFixed(2)}</td>
            `;
        } else if (modelType === 'desertion') {
            row.innerHTML += `
                <td>${result.desertion_probability ? (result.desertion_probability * 100).toFixed(1) + '%' : 'N/A'}</td>
                <td>${getRiskLevelBadge(result.risk_level || 'Unknown')}</td>
                <td>${result.primary_churn_reason || 'N/A'}</td>
                <td>${result.retention_strategy || 'N/A'}</td>
                <td>${formatCurrency(result.retention_cost || 0)}</td>
            `;
        }
        
        tableBody.appendChild(row);
    });
    
    // Create statistics and chart
    createStatistics(results, modelType);
}

// Add helper functions for badges and formatting
function getRiskLevelBadge(level) {
    let badgeClass = 'bg-secondary';
    
    if (level === 'Low' || level === 'Thấp') {
        badgeClass = 'bg-success';
    } else if (level === 'Medium' || level === 'Trung bình') {
        badgeClass = 'bg-warning';
    } else if (level === 'High' || level === 'Cao') {
        badgeClass = 'bg-danger';
    }
    
    return `<span class="badge ${badgeClass}">${level}</span>`;
}

function getActionBadge(action) {
    let badgeClass = 'bg-secondary';
    let actionText = action;
    
    // Application model actions
    if (action === 'Approve' || action === 'Increase') {
        badgeClass = 'bg-success';
        actionText = action === 'Approve' ? 'Chấp nhận' : 'Tăng hạn mức';
    } else if (action === 'Review' || action === 'Maintain') {
        badgeClass = 'bg-warning';
        actionText = action === 'Review' ? 'Xem xét' : 'Giữ nguyên';
    } else if (action === 'Reject' || action === 'Decrease') {
        badgeClass = 'bg-danger';
        actionText = action === 'Reject' ? 'Từ chối' : 'Giảm hạn mức';
    }
    
    return `<span class="badge ${badgeClass}">${actionText}</span>`;
}

function getCollectionStrategyBadge(strategy) {
    let badgeClass = 'bg-secondary';
    
    switch (strategy) {
        case 'Champion':
            badgeClass = 'bg-success';
            break;
        case 'Negotiable':
            badgeClass = 'bg-primary';
            break;
        case 'Cure':
            badgeClass = 'bg-info';
            break;
        case 'Restructure':
            badgeClass = 'bg-warning';
            break;
        case 'Legal':
            badgeClass = 'bg-danger';
            break;
        case 'Write-off':
            badgeClass = 'bg-dark';
            break;
    }
    
    return `<span class="badge ${badgeClass}">${strategy}</span>`;
}

// Add statistics and chart creation
function createStatistics(results, modelType) {
    const statsTableBody = document.getElementById('statsTableBody');
    statsTableBody.innerHTML = '';
    
    // Create distribution chart based on model type
    let chartData = {
        labels: [],
        datasets: [{
            label: '',
            data: [],
            backgroundColor: [
                'rgba(54, 162, 235, 0.6)',
                'rgba(255, 206, 86, 0.6)',
                'rgba(75, 192, 192, 0.6)',
                'rgba(153, 102, 255, 0.6)',
                'rgba(255, 159, 64, 0.6)'
            ]
        }]
    };
    
    // Calculate statistics based on model type
    if (modelType === 'application') {
        // Credit score distribution
        const scores = results.map(r => (r.risk_profile || {}).credit_score).filter(s => s);
        const avgScore = scores.length ? scores.reduce((a, b) => a + b, 0) / scores.length : 0;
        
        addStatRow('Số lượng khách hàng', results.length);
        addStatRow('Điểm trung bình', avgScore.toFixed(0));
        
        // Risk level distribution
        const riskLevels = {};
        results.forEach(r => {
            const level = (r.risk_profile || {}).risk_level || 'Unknown';
            riskLevels[level] = (riskLevels[level] || 0) + 1;
        });
        
        chartData.labels = Object.keys(riskLevels);
        chartData.datasets[0].label = 'Phân bố mức độ rủi ro';
        chartData.datasets[0].data = Object.values(riskLevels);
        
    } else if (modelType === 'behavior') {
        // Calculate average limit change
        let totalCurrentLimit = 0;
        let totalSuggestedLimit = 0;
        const actions = {};
        
        results.forEach(r => {
            const rec = r.credit_recommendation || {};
            totalCurrentLimit += rec.current_limit || 0;
            totalSuggestedLimit += rec.suggested_limit || 0;
            
            const action = rec.suggested_action || 'Unknown';
            actions[action] = (actions[action] || 0) + 1;
        });
        
        const avgCurrentLimit = results.length ? totalCurrentLimit / results.length : 0;
        const avgSuggestedLimit = results.length ? totalSuggestedLimit / results.length : 0;
        const totalChange = totalSuggestedLimit - totalCurrentLimit;
        const changePercent = totalCurrentLimit > 0 ? (totalChange / totalCurrentLimit * 100).toFixed(1) : '0.0';
        
        addStatRow('Số lượng khách hàng', results.length);
        addStatRow('Hạn mức trung bình hiện tại', formatCurrency(avgCurrentLimit));
        addStatRow('Hạn mức trung bình đề xuất', formatCurrency(avgSuggestedLimit));
        addStatRow('Thay đổi tổng thể', `${formatCurrency(totalChange)} (${changePercent}%)`);
        
        // Create chart for actions
        chartData.labels = Object.keys(actions);
        chartData.datasets[0].label = 'Phân bố đề xuất';
        chartData.datasets[0].data = Object.values(actions);
        
    } else if (modelType === 'collections') {
        // Collection statistics
        let totalOutstanding = 0;
        let totalExpectedRecovery = 0;
        const strategies = {};
        
        results.forEach(r => {
            totalOutstanding += r.outstanding_amount || 0;
            totalExpectedRecovery += r.expected_recovery_value || 0;
            
            const strategy = r.collection_strategy || 'Unknown';
            strategies[strategy] = (strategies[strategy] || 0) + 1;
        });
        
        const recoveryRate = totalOutstanding > 0 ? (totalExpectedRecovery / totalOutstanding * 100).toFixed(1) : '0.0';
        
        addStatRow('Số lượng tài khoản', results.length);
        addStatRow('Tổng số tiền nợ', formatCurrency(totalOutstanding));
        addStatRow('Tổng dự kiến thu hồi', formatCurrency(totalExpectedRecovery));
        addStatRow('Tỷ lệ thu hồi dự kiến', `${recoveryRate}%`);
        
        // Create chart for strategies
        chartData.labels = Object.keys(strategies);
        chartData.datasets[0].label = 'Phân bố chiến lược thu hồi';
        chartData.datasets[0].data = Object.values(strategies);
        
    } else if (modelType === 'desertion') {
        // Desertion statistics
        let totalProbability = 0;
        let totalCost = 0;
        const riskLevels = {};
        
        results.forEach(r => {
            totalProbability += r.desertion_probability || 0;
            totalCost += r.retention_cost || 0;
            
            const level = r.risk_level || 'Unknown';
            riskLevels[level] = (riskLevels[level] || 0) + 1;
        });
        
        const avgProbability = results.length ? (totalProbability / results.length * 100).toFixed(1) : '0.0';
        const avgCost = results.length ? totalCost / results.length : 0;
        
        addStatRow('Số lượng khách hàng', results.length);
        addStatRow('Xác suất rời bỏ trung bình', `${avgProbability}%`);
        addStatRow('Chi phí giữ chân trung bình', formatCurrency(avgCost));
        addStatRow('Tổng chi phí giữ chân', formatCurrency(totalCost));
        
        // Create chart for risk levels
        chartData.labels = Object.keys(riskLevels);
        chartData.datasets[0].label = 'Phân bố mức độ rủi ro';
        chartData.datasets[0].data = Object.values(riskLevels);
    }
    
    // Create and render the chart
    const ctx = document.getElementById('distributionChart').getContext('2d');
    
    // Destroy existing chart if any
    if (window.batchChart) {
        window.batchChart.destroy();
    }
    
    window.batchChart = new Chart(ctx, {
        type: 'pie',
        data: chartData,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Phân bố kết quả'
                }
            }
        }
    });
    
    function addStatRow(label, value) {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${label}</td><td>${value}</td>`;
        statsTableBody.appendChild(row);
    }
}

// Format currency consistently
function formatCurrency(value) {
    return new Intl.NumberFormat('vi-VN', { 
        style: 'currency', 
        currency: 'VND',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

// Add export functionality
function exportResults() {
    if (!window.batchResults || !window.batchResults.length) {
        alert('Không có dữ liệu để xuất');
        return;
    }
    
    // Convert results to CSV
    let csvContent = "data:text/csv;charset=utf-8,";
    
    // Get headers based on model type
    const headers = ["customer_id"];
    const modelType = window.batchModelType;
    
    if (modelType === 'application') {
        headers.push("credit_score", "default_probability", "risk_level", "suggested_action");
    } else if (modelType === 'behavior') {
        headers.push("credit_score", "current_limit", "suggested_limit", "limit_change", "suggested_action");
    } else if (modelType === 'collections') {
        headers.push("priority_score", "collection_strategy", "outstanding_amount", "expected_recovery", "recovery_roi");
    } else if (modelType === 'desertion') {
        headers.push("desertion_probability", "risk_level", "primary_reason", "retention_strategy", "retention_cost");
    }
    
    csvContent += headers.join(",") + "\n";
    
    // Add data rows
    window.batchResults.forEach(result => {
        const row = [];
        row.push(result.customer_id || "");
        
        if (modelType === 'application') {
            const profile = result.risk_profile || {};
            row.push(profile.credit_score || "");
            row.push(profile.default_probability || "");
            row.push(profile.risk_level || "");
            row.push(profile.suggested_action || "");
        } else if (modelType === 'behavior') {
            const rec = result.credit_recommendation || {};
            row.push(rec.credit_score || "");
            row.push(rec.current_limit || "");
            row.push(rec.suggested_limit || "");
            row.push((rec.suggested_limit || 0) - (rec.current_limit || 0));
            row.push(rec.suggested_action || "");
        } else if (modelType === 'collections') {
            row.push(result.priority_score || "");
            row.push(result.collection_strategy || "");
            row.push(result.outstanding_amount || "");
            row.push(result.expected_recovery_value || "");
            row.push(result.recovery_roi || "");
        } else if (modelType === 'desertion') {
            row.push(result.desertion_probability || "");
            row.push(result.risk_level || "");
            row.push(result.primary_churn_reason || "");
            row.push(result.retention_strategy || "");
            row.push(result.retention_cost || "");
        }
        
        csvContent += row.join(",") + "\n";
    });
    
    // Create download link
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `batch_results_${modelType}_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    
    // Trigger download
    link.click();
    document.body.removeChild(link);
}

// Add the handleFileUpload function for processing batch file data
function handleFileUpload() {
    const fileInput = document.getElementById('fileUpload');
    const modelType = document.getElementById('fileModelType').value;
    const hasHeader = document.getElementById('hasHeader').checked;
    
    // Validate input
    if (!modelType) {
        alert('Vui lòng chọn loại mô hình');
        return;
    }
    
    if (!fileInput.files || fileInput.files.length === 0) {
        alert('Vui lòng chọn tệp để tải lên');
        return;
    }
    
    const file = fileInput.files[0];
    
    // Show loading state
    const submitBtn = document.querySelector('#fileUploadForm button[type="submit"]');
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Đang xử lý...';
    submitBtn.disabled = true;
    
    // Clear previous results
    clearResults();
    
    // Show Processing notification
    showProcessingNotification();
    
    // Process the file
    if (file.name.endsWith('.csv')) {
        Papa.parse(file, {
            header: hasHeader,
            complete: function(results) {
                if (results.data && results.data.length > 0) {
                    console.log(`Parsed ${results.data.length} rows from CSV`);
                    processFileData(results.data, modelType);
                } else {
                    showError('Tệp CSV không chứa dữ liệu hợp lệ');
                    resetFileForm();
                }
            },
            error: function(error) {
                showError(`Lỗi khi đọc tệp CSV: ${error}`);
                resetFileForm();
            }
        });
    } else {
        showError('Loại tệp chưa được hỗ trợ. Vui lòng sử dụng tệp CSV.');
        resetFileForm();
    }
}

// Reset the file upload form
function resetFileForm() {
    const submitBtn = document.querySelector('#fileUploadForm button[type="submit"]');
    submitBtn.innerHTML = 'Xử lý hàng loạt';
    submitBtn.disabled = false;
}

// Process data from file
function processFileData(data, modelType) {
    try {
        console.log("Processing file data for model type:", modelType);
        
        // Determine the endpoint based on model type
        const endpoint = getBatchEndpoint(modelType);
        
        // Process data with validation
        let processedResult;
        if (modelType === 'application') {
            processedResult = processApplicationData(data);
        } else if (modelType === 'behavior') {
            processedResult = processBehaviorData(data);
        } else if (modelType === 'collections') {
            processedResult = processCollectionsData(data);
        } else if (modelType === 'desertion') {
            processedResult = processDesertionData(data);
        }
        
        // Check for validation errors
        if (processedResult.errors && processedResult.errors.length > 0) {
            hideProcessingNotification();
            showValidationErrors(processedResult.errors);
            resetFileForm();
            return;
        }
        
        // Prepare final data for API - Special handling for collections
        let processedData;
        
        if (modelType === 'collections') {
            // Collections endpoint expects a direct array, not wrapped in a 'customers' object
            processedData = processedResult.processedData;
        } else {
            processedData = { customers: processedResult.processedData };
        }
        
        console.log("Processed data for API:", processedData);
        
        // Send data to API
        callApi(endpoint, 'POST', processedData)
            .then(response => {
                hideProcessingNotification();
                
                // Special handling for collections response
                if (modelType === 'collections' && !response.prioritized_accounts) {
                    // If the response doesn't have prioritized_accounts, transform it
                    response = { prioritized_accounts: response };
                }
                
                displayBatchResults(response, modelType);
            })
            .catch(error => {
                hideProcessingNotification();
                showError(`Lỗi khi gọi API ${endpoint}: ${formatErrorMessage(error)}`);
                console.error('API error details:', error);
            })
            .finally(() => {
                resetFileForm();
            });
    } catch (error) {
        hideProcessingNotification();
        showError(formatErrorMessage(error));
        resetFileForm();
    }
}

// Add the handleManualInput function for processing manual data
function handleManualInput() {
    const customerIDs = document.getElementById('customerIDs').value;
    const modelType = document.getElementById('manualModelType').value;
    
    // Validate input
    if (!modelType) {
        alert('Vui lòng chọn loại mô hình');
        return;
    }
    
    if (!customerIDs.trim()) {
        alert('Vui lòng nhập danh sách ID khách hàng');
        return;
    }
    
    // Split IDs
    const ids = customerIDs.split(/\r?\n/).filter(id => id.trim());
    
    if (ids.length === 0) {
        alert('Không tìm thấy ID khách hàng hợp lệ');
        return;
    }
    
    // Show loading state
    const submitBtn = document.querySelector('#manualInputForm button[type="submit"]');
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Đang xử lý...';
    submitBtn.disabled = true;
    
    // Clear previous results
    clearResults();
    
    // Show Processing notification
    showProcessingNotification();
    
    // Format data for API - With special handling for collections
    let data;
    
    if (modelType === 'collections') {
        // For collections, we need to format differently since the endpoint expects a list directly
        data = ids.map(id => ({ 
            customer_id: id,
            days_past_due: 30, // Default values
            outstanding_amount: 1000000,
            number_of_contacts: 1,
            previous_late_payments: 1,
            promised_payment_amount: 500000,
            broken_promises: 0,
            months_on_book: 12,
            last_payment_amount: 300000
        }));
        
        console.log("Sending collections data:", data);
    } else {
        // Standard format for other models
        data = { customers: ids.map(id => ({ customer_id: id })) };
    }
    
    console.log("Sending to API:", data);
    
    // Determine the endpoint based on model type
    const endpoint = getBatchEndpoint(modelType);
    
    // Send data to API
    callApi(endpoint, 'POST', data)
        .then(response => {
            hideProcessingNotification();
            displayBatchResults(response, modelType);
        })
        .catch(error => {
            hideProcessingNotification();
            showError(formatErrorMessage(error));
        })
        .finally(() => {
            submitBtn.innerHTML = 'Xử lý hàng loạt';
            submitBtn.disabled = false;
        });
}

// Add the getBatchEndpoint function
function getBatchEndpoint(modelType) {
    switch(modelType) {
        case 'application':
            return 'batch/application-score/';
        case 'behavior':
            return 'batch/behavior-score/';
        case 'collections':
            // Use the correct endpoint for collections
            return 'collections-prioritize/'; // Remove 'batch/' prefix if not needed
        case 'desertion':
            return 'batch/desertion-strategy/';
        default:
            throw new Error(`Invalid model type: ${modelType}`);
    }
}

// Functions to process different types of data
function processApplicationData(data) {
    const processedData = [];
    const errors = [];
    
    data.forEach((row, index) => {
        const { result, validationErrors } = normalizeRecord(row, [
            'customer_id', 'age', 'income', 'employment_length', 'debt_to_income', 
            'credit_history_length', 'number_of_debts', 'number_of_delinquent_debts', 'homeowner'
        ]);
        
        processedData.push(result);
        
        if (validationErrors.length > 0) {
            errors.push(`Dòng ${index + 1}: ${validationErrors.join(', ')}`);
        }
    });
    
    return { processedData, errors };
}

function processBehaviorData(data) {
    const processedData = [];
    const errors = [];
    
    data.forEach((row, index) => {
        const { result, validationErrors } = normalizeRecord(row, [
            'customer_id', 'current_balance', 'average_monthly_payment', 'payment_ratio',
            'number_of_late_payments', 'months_since_last_late_payment', 
            'number_of_credit_inquiries', 'current_limit', 'average_utilization'
        ]);
        
        processedData.push(result);
        
        if (validationErrors.length > 0) {
            errors.push(`Dòng ${index + 1}: ${validationErrors.join(', ')}`);
        }
    });
    
    return { processedData, errors };
}

function processCollectionsData(data) {
    const processedData = [];
    const errors = [];
    
    data.forEach((row, index) => {
        try {
            // Special validation for collections data
            if (!row.customer_id) {
                errors.push(`Dòng ${index + 1}: Thiếu ID khách hàng`);
                return;
            }
            
            if (!row.outstanding_amount && row.outstanding_amount !== 0) {
                errors.push(`Dòng ${index + 1}: Thiếu số tiền nợ cho khách hàng ${row.customer_id}`);
                return;
            }
            
            const { result, validationErrors } = normalizeRecord(row, [
                'customer_id', 'days_past_due', 'outstanding_amount', 'number_of_contacts',
                'previous_late_payments', 'promised_payment_amount', 'broken_promises',
                'months_on_book', 'last_payment_amount'
            ]);
            
            // Ensure all numbers are proper numbers
            Object.keys(result).forEach(key => {
                if (key !== 'customer_id' && (isNaN(result[key]) || result[key] === null)) {
                    result[key] = 0; // Set default values for missing numeric fields
                }
            });
            
            processedData.push(result);
            
            if (validationErrors.length > 0) {
                errors.push(`Dòng ${index + 1}: ${validationErrors.join(', ')}`);
            }
        } catch (e) {
            console.error(`Error processing row ${index}:`, e, row);
            errors.push(`Dòng ${index + 1}: Lỗi xử lý dữ liệu - ${e.message}`);
        }
    });
    
    return { processedData, errors };
}

function processDesertionData(data) {
    const processedData = [];
    const errors = [];
    
    data.forEach((row, index) => {
        const { result, validationErrors } = normalizeRecord(row, [
            'customer_id', 'months_to_maturity', 'total_relationship_value', 'number_of_products',
            'satisfaction_score', 'number_of_complaints', 'months_since_last_interaction',
            'age', 'tenure_months', 'monthly_average_balance'
        ]);
        
        processedData.push(result);
        
        if (validationErrors.length > 0) {
            errors.push(`Dòng ${index + 1}: ${validationErrors.join(', ')}`);
        }
    });
    
    return { processedData, errors };
}

// Helper to normalize record keys
function normalizeRecord(record, expectedFields) {
    const result = {};
    const validationErrors = [];
    
    // Map fields to expected names (handling case insensitivity and variations)
    expectedFields.forEach(field => {
        // Try to find the field
        let value = null;
        
        // Try exact match
        if (field in record) {
            value = record[field];
        } 
        // Try case-insensitive match
        else {
            const fieldLower = field.toLowerCase();
            const matchingKey = Object.keys(record).find(k => k.toLowerCase() === fieldLower);
            if (matchingKey) {
                value = record[matchingKey];
            }
        }
        
        // Convert value types
        if (value !== null) {
            // Convert to appropriate type
            if (field === 'customer_id') {
                result[field] = String(value);
            } else if (field === 'homeowner') {
                result[field] = parseInt(value);
            } else if (['payment_ratio', 'debt_to_income', 'average_utilization'].includes(field)) {
                result[field] = parseFloat(value);
            } else if (field.includes('amount') || field.includes('balance') || field.includes('income') || field.includes('value') || field === 'current_limit') {
                result[field] = parseFloat(value);
            } else {
                result[field] = parseFloat(value);
            }
            
            // Perform field-specific validation
            if (field === 'age' && result[field] < 18) {
                validationErrors.push(`Tuổi khách hàng ${result.customer_id || ''} phải lớn hơn hoặc bằng 18 (hiện tại: ${result[field]})`);
            }
        } else {
            console.warn(`Field ${field} not found in record`, record);
            // Use default values if field is missing
            if (field === 'customer_id') {
                result[field] = 'UNKNOWN';
            } else if (field === 'age') {
                result[field] = 18; // Set minimum valid age as default
            } else {
                result[field] = 0;
            }
        }
    });
    
    return { result, validationErrors };
}

// Add new UI utility functions
function clearResults() {
    document.getElementById('resultsCard').style.display = 'none';
    if (window.batchChart) {
        window.batchChart.destroy();
        window.batchChart = null;
    }
}

function showProcessingNotification() {
    // Create a processing overlay if it doesn't exist
    if (!document.getElementById('processingOverlay')) {
        const overlay = document.createElement('div');
        overlay.id = 'processingOverlay';
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100%';
        overlay.style.height = '100%';
        overlay.style.backgroundColor = 'rgba(0,0,0,0.5)';
        overlay.style.display = 'flex';
        overlay.style.justifyContent = 'center';
        overlay.style.alignItems = 'center';
        overlay.style.zIndex = '9999';
        
        const content = document.createElement('div');
        content.className = 'bg-white p-4 rounded shadow-lg text-center';
        content.innerHTML = `
            <div class="spinner-border text-primary mb-3" role="status" style="width: 3rem; height: 3rem;">
                <span class="visually-hidden">Đang xử lý...</span>
            </div>
            <h4>Đang xử lý dữ liệu</h4>
            <p class="mb-0">Vui lòng đợi trong giây lát...</p>
        `;
        
        overlay.appendChild(content);
        document.body.appendChild(overlay);
    } else {
        document.getElementById('processingOverlay').style.display = 'flex';
    }
}

function hideProcessingNotification() {
    const overlay = document.getElementById('processingOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

function showError(message) {
    console.error("API Error:", message);
    
    // Show error in results card
    const resultsCard = document.getElementById('resultsCard');
    resultsCard.style.display = 'block';
    
    // Format the message for display
    let displayMessage = message;
    
    // If the message is just "[object Object]", replace with something more useful
    if (message === "[object Object]") {
        displayMessage = "Lỗi không xác định từ API. Vui lòng kiểm tra console để biết thêm chi tiết.";
    }
    
    resultsCard.querySelector('.card-body').innerHTML = `
        <div class="alert alert-danger">
            <h5>Lỗi xảy ra</h5>
            <p>${displayMessage}</p>
            <p>Vui lòng kiểm tra dữ liệu đầu vào và thử lại.</p>
            <div class="mt-3">
                <button class="btn btn-outline-secondary btn-sm" onclick="showDebugInfo()">Hiển thị thông tin debug</button>
            </div>
            <div id="debugInfo" class="mt-3" style="display: none;">
                <small class="text-muted">Browser Console: Nhấn F12 để mở Developer Tools và xem thêm chi tiết</small>
            </div>
        </div>
    `;
    
    resultsCard.scrollIntoView({ behavior: 'smooth' });
}

// Add a function to show debug info
function showDebugInfo() {
    const debugElement = document.getElementById('debugInfo');
    if (debugElement) {
        debugElement.style.display = 'block';
    }
}

// Enhance the API caller function to handle errors better
function callApi(endpoint, method = 'GET', data = null) {
    const url = `/api/proxy/${endpoint}`;
    
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (data && method === 'POST') {
        options.body = JSON.stringify(data);
    }
    
    console.log(`Calling API endpoint: ${url}`);
    console.log('Request options:', options);
    
    return fetch(url, options)
        .then(response => {
            // Save the status code for debugging
            const statusCode = response.status;
            
            if (!response.ok) {
                console.error(`API error status: ${statusCode} for endpoint ${endpoint}`);
                
                // Try to get more detailed error information
                return response.text()  // Get raw text first instead of assuming JSON
                    .then(text => {
                        console.error('API error raw response:', text);
                        
                        try {
                            // Try to parse as JSON
                            const errorData = JSON.parse(text);
                            console.error('API error parsed response:', errorData);
                            
                            // Special handling for 422 errors which have validation details
                            if (statusCode === 422 && errorData.detail) {
                                let errorMessage = "Lỗi dữ liệu: ";
                                
                                if (Array.isArray(errorData.detail)) {
                                    errorMessage += errorData.detail.map(err => {
                                        return `${err.loc.join('.')} - ${err.msg}`;
                                    }).join('; ');
                                } else {
                                    errorMessage += errorData.detail;
                                }
                                
                                throw new Error(errorMessage);
                            }
                            
                            // Create an error with the details
                            throw new Error(errorData.detail || `HTTP error: ${statusCode}`);
                        } catch (jsonError) {
                            // If not valid JSON, return the text
                            if (jsonError instanceof SyntaxError) {
                                throw new Error(`HTTP error ${statusCode}: ${text || response.statusText}`);
                            }
                            throw jsonError;
                        }
                    });
            }
            
            // For successful responses, try to parse as JSON
            return response.text().then(text => {
                if (!text) return {}; // Handle empty responses
                try {
                    return JSON.parse(text);
                } catch (e) {
                    console.warn('Response is not valid JSON:', text);
                    return { raw_response: text };
                }
            });
        })
        .catch(error => {
            console.error('API call failed:', error);
            throw error;
        });
}

// Add the formatErrorMessage function that was referenced but missing

function formatErrorMessage(error) {
    // Check if it's a JavaScript Error object
    if (error instanceof Error) {
        return error.message;
    }
    
    // If it's a structured API error response
    if (error && typeof error === 'object') {
        // Try to extract message from common API error formats
        if (error.message) return error.message;
        if (error.error) return typeof error.error === 'string' ? error.error : JSON.stringify(error.error);
        if (error.detail) return error.detail;
        
        // If we have a structured object, convert it to a string for display
        try {
            return JSON.stringify(error);
        } catch (e) {
            return "Lỗi không xác định từ API";
        }
    }
    
    // If it's just a string
    if (typeof error === 'string') {
        return error;
    }
    
    // Default fallback
    return "Đã xảy ra lỗi không xác định khi gọi API";
}

// Add validation to ensure the data meets API requirements

// Update normalizeRecord function to add validation
function normalizeRecord(record, expectedFields) {
    const result = {};
    const validationErrors = [];
    
    // Map fields to expected names (handling case insensitivity and variations)
    expectedFields.forEach(field => {
        // Try to find the field
        let value = null;
        
        // Try exact match
        if (field in record) {
            value = record[field];
        } 
        // Try case-insensitive match
        else {
            const fieldLower = field.toLowerCase();
            const matchingKey = Object.keys(record).find(k => k.toLowerCase() === fieldLower);
            if (matchingKey) {
                value = record[matchingKey];
            }
        }
        
        // Convert value types
        if (value !== null) {
            // Convert to appropriate type
            if (field === 'customer_id') {
                result[field] = String(value);
            } else if (field === 'homeowner') {
                result[field] = parseInt(value);
            } else if (['payment_ratio', 'debt_to_income', 'average_utilization'].includes(field)) {
                result[field] = parseFloat(value);
            } else if (field.includes('amount') || field.includes('balance') || field.includes('income') || field.includes('value') || field === 'current_limit') {
                result[field] = parseFloat(value);
            } else {
                result[field] = parseFloat(value);
            }
            
            // Perform field-specific validation
            if (field === 'age' && result[field] < 18) {
                validationErrors.push(`Tuổi khách hàng ${result.customer_id || ''} phải lớn hơn hoặc bằng 18 (hiện tại: ${result[field]})`);
            }
        } else {
            console.warn(`Field ${field} not found in record`, record);
            // Use default values if field is missing
            if (field === 'customer_id') {
                result[field] = 'UNKNOWN';
            } else if (field === 'age') {
                result[field] = 18; // Set minimum valid age as default
            } else {
                result[field] = 0;
            }
        }
    });
    
    return { result, validationErrors };
}

// Update the processApplicationData function to include validation
function processApplicationData(data) {
    const processedData = [];
    const errors = [];
    
    data.forEach((row, index) => {
        const { result, validationErrors } = normalizeRecord(row, [
            'customer_id', 'age', 'income', 'employment_length', 'debt_to_income', 
            'credit_history_length', 'number_of_debts', 'number_of_delinquent_debts', 'homeowner'
        ]);
        
        processedData.push(result);
        
        if (validationErrors.length > 0) {
            errors.push(`Dòng ${index + 1}: ${validationErrors.join(', ')}`);
        }
    });
    
    return { processedData, errors };
}

// Update the processBehaviorData function similarly
function processBehaviorData(data) {
    const processedData = [];
    const errors = [];
    
    data.forEach((row, index) => {
        const { result, validationErrors } = normalizeRecord(row, [
            'customer_id', 'current_balance', 'average_monthly_payment', 'payment_ratio',
            'number_of_late_payments', 'months_since_last_late_payment', 
            'number_of_credit_inquiries', 'current_limit', 'average_utilization'
        ]);
        
        processedData.push(result);
        
        if (validationErrors.length > 0) {
            errors.push(`Dòng ${index + 1}: ${validationErrors.join(', ')}`);
        }
    });
    
    return { processedData, errors };
}

// Update the processCollectionsData function similarly
function processCollectionsData(data) {
    const processedData = [];
    const errors = [];
    
    data.forEach((row, index) => {
        try {
            // Special validation for collections data
            if (!row.customer_id) {
                errors.push(`Dòng ${index + 1}: Thiếu ID khách hàng`);
                return;
            }
            
            if (!row.outstanding_amount && row.outstanding_amount !== 0) {
                errors.push(`Dòng ${index + 1}: Thiếu số tiền nợ cho khách hàng ${row.customer_id}`);
                return;
            }
            
            const { result, validationErrors } = normalizeRecord(row, [
                'customer_id', 'days_past_due', 'outstanding_amount', 'number_of_contacts',
                'previous_late_payments', 'promised_payment_amount', 'broken_promises',
                'months_on_book', 'last_payment_amount'
            ]);
            
            // Ensure all numbers are proper numbers
            Object.keys(result).forEach(key => {
                if (key !== 'customer_id' && (isNaN(result[key]) || result[key] === null)) {
                    result[key] = 0; // Set default values for missing numeric fields
                }
            });
            
            processedData.push(result);
            
            if (validationErrors.length > 0) {
                errors.push(`Dòng ${index + 1}: ${validationErrors.join(', ')}`);
            }
        } catch (e) {
            console.error(`Error processing row ${index}:`, e, row);
            errors.push(`Dòng ${index + 1}: Lỗi xử lý dữ liệu - ${e.message}`);
        }
    });
    
    return { processedData, errors };
}

// Update the processDesertionData function similarly
function processDesertionData(data) {
    const processedData = [];
    const errors = [];
    
    data.forEach((row, index) => {
        const { result, validationErrors } = normalizeRecord(row, [
            'customer_id', 'months_to_maturity', 'total_relationship_value', 'number_of_products',
            'satisfaction_score', 'number_of_complaints', 'months_since_last_interaction',
            'age', 'tenure_months', 'monthly_average_balance'
        ]);
        
        processedData.push(result);
        
        if (validationErrors.length > 0) {
            errors.push(`Dòng ${index + 1}: ${validationErrors.join(', ')}`);
        }
    });
    
    return { processedData, errors };
}

// Add a function to display validation errors
function showValidationErrors(errors) {
    // Show error in results card
    const resultsCard = document.getElementById('resultsCard');
    resultsCard.style.display = 'block';
    
    resultsCard.querySelector('.card-body').innerHTML = `
        <div class="alert alert-danger">
            <h5>Lỗi dữ liệu</h5>
            <p>Dữ liệu đầu vào có lỗi cần khắc phục trước khi xử lý:</p>
            <ul class="mt-3">
                ${errors.map(err => `<li>${err}</li>`).join('')}
            </ul>
            <p class="mt-3">Vui lòng kiểm tra và sửa dữ liệu rồi thử lại.</p>
        </div>
    `;
    
    resultsCard.scrollIntoView({ behavior: 'smooth' });
}

// Update the template generation function to ensure valid data
function downloadTemplate(type = 'file') {
    // ...existing code...
    
    switch(modelType) {
        case 'application':
            csvContent = "customer_id,age,income,employment_length,debt_to_income,credit_history_length,number_of_debts,number_of_delinquent_debts,homeowner\n";
            csvContent += "CUS000123,35,50000,5.5,0.25,7,2,0,1\n";
            csvContent += "CUS000124,42,60000,8.0,0.15,12,1,0,1\n";
            csvContent += "CUS000125,29,35000,3.0,0.35,4,3,1,0\n";
            filename = "application_template.csv";
            break;
        // ...existing code...
    }
    
    // ...existing code...
}

// ...existing code...