document.addEventListener('DOMContentLoaded', function() {
    // Add account event
    document.getElementById('addAccount').addEventListener('click', function() {
        addAccountToTable();
    });
    
    // Form submission handler
    document.getElementById('collectionsForm').addEventListener('submit', function(e) {
        e.preventDefault();
        processCollectionsData();
    });
    
    // Load sample data
    document.getElementById('loadSample').addEventListener('click', function() {
        loadSampleData();
    });
    
    // Initialize accounts array
    window.accounts = [];
});

function addAccountToTable() {
    // Get form values
    const account = {
        customer_id: document.getElementById('customer_id').value,
        days_past_due: parseInt(document.getElementById('days_past_due').value),
        outstanding_amount: parseFloat(document.getElementById('outstanding_amount').value),
        number_of_contacts: parseInt(document.getElementById('number_of_contacts').value),
        previous_late_payments: parseInt(document.getElementById('previous_late_payments').value),
        promised_payment_amount: parseFloat(document.getElementById('promised_payment_amount').value),
        broken_promises: parseInt(document.getElementById('broken_promises').value),
        months_on_book: parseInt(document.getElementById('months_on_book').value),
        last_payment_amount: parseFloat(document.getElementById('last_payment_amount').value)
    };
    
    // Validate all fields are filled
    for (let key in account) {
        if (!account[key] && account[key] !== 0) {
            alert(`Vui lòng nhập đầy đủ thông tin (${key} đang thiếu)`);
            return;
        }
    }
    
    // Add to accounts array
    window.accounts.push(account);
    
    // Update table
    updateAccountsTable();
    
    // Clear form for next account
    document.getElementById('customer_id').value = '';
    document.getElementById('customer_id').focus();
}

function updateAccountsTable() {
    const tableBody = document.getElementById('accountsTableBody');
    tableBody.innerHTML = '';
    
    window.accounts.forEach((account, index) => {
        const row = document.createElement('tr');
        
        // Add cells
        row.innerHTML = `
            <td>${account.customer_id}</td>
            <td>${account.days_past_due}</td>
            <td>${formatCurrency(account.outstanding_amount)}</td>
            <td>${account.number_of_contacts}</td>
            <td>${account.previous_late_payments}</td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="removeAccount(${index})">
                    <i class="bi bi-trash"></i> Xóa
                </button>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}

function removeAccount(index) {
    window.accounts.splice(index, 1);
    updateAccountsTable();
}

function processCollectionsData() {
    // Ensure we have accounts to process
    if (window.accounts.length === 0) {
        // If no accounts in the table, try to add the current form data
        addAccountToTable();
        
        // Check again
        if (window.accounts.length === 0) {
            alert('Vui lòng thêm ít nhất một tài khoản để phân tích');
            return;
        }
    }
    
    // Show loading spinner
    const submitBtn = document.querySelector('button[type="submit"]');
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Đang xử lý...';
    submitBtn.disabled = true;
    
    // Make sure all values are numbers (except customer_id)
    const processedAccounts = window.accounts.map(account => {
        const processed = { ...account };
        for (const key in processed) {
            if (key !== 'customer_id' && typeof processed[key] !== 'number') {
                processed[key] = parseFloat(processed[key]) || 0;
            }
        }
        return processed;
    });
    
    console.log('Sending collections data:', processedAccounts);
    
    // Send API request - Note: The collections API wants the array directly, not wrapped in an object
    callApi('collections-prioritize/', 'POST', processedAccounts)
        .then(data => {
            console.log('Collections API response:', data);
            
            // Format response if needed
            let formattedData = data;
            if (!data.prioritized_accounts && Array.isArray(data)) {
                formattedData = { prioritized_accounts: data };
            }
            
            displayResults(formattedData);
        })
        .catch(error => {
            console.error('Error processing collections:', error);
            
            let errorMessage = 'Đã xảy ra lỗi khi xử lý yêu cầu. Vui lòng thử lại sau.';
            
            // Try to extract a more specific error message
            if (error && error.message) {
                errorMessage = error.message;
            } else if (typeof error === 'string') {
                errorMessage = error;
            }
            
            // Display error message to user
            alert(errorMessage);
            
            // Log detailed error for debugging
            console.error('Collections API error details:', error);
        })
        .finally(() => {
            // Reset button
            submitBtn.innerHTML = 'Phân tích';
            submitBtn.disabled = false;
        });
}

// Add improved callApi function that better handles errors
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
    
    console.log(`Collections API call to ${url}`, options);
    
    return fetch(url, options)
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => {
                    console.error(`API error ${response.status}: ${text}`);
                    
                    try {
                        // Try parsing as JSON first
                        const errorData = JSON.parse(text);
                        throw new Error(errorData.detail || `Server error: ${response.status}`);
                    } catch (e) {
                        // If parsing fails, use text or status
                        throw new Error(text || `Server error: ${response.status}`);
                    }
                });
            }
            return response.json();
        });
}

function displayResults(data) {
    // Show results section
    document.getElementById('resultsSection').style.display = 'block';
    
    // Get prioritized accounts
    const prioritizedAccounts = data.prioritized_accounts || [];
    
    // Clear previous results
    const resultsTableBody = document.getElementById('priorityTableBody');
    resultsTableBody.innerHTML = '';
    
    // Add rows to results table
    prioritizedAccounts.forEach((account, index) => {
        const row = document.createElement('tr');
        
        // Add styling based on priority
        if (index === 0) {
            row.className = 'table-success';
        } else if (index < 3) {
            row.className = 'table-warning';
        }
        
        // Format strategy badge
        let strategyBadge = '';
        
        switch (account.collection_strategy) {
            case 'Champion':
                strategyBadge = '<span class="badge bg-success">Champion</span>';
                break;
            case 'Negotiable':
                strategyBadge = '<span class="badge bg-primary">Negotiable</span>';
                break;
            case 'Cure':
                strategyBadge = '<span class="badge bg-info">Cure</span>';
                break;
            case 'Restructure':
                strategyBadge = '<span class="badge bg-warning">Restructure</span>';
                break;
            case 'Legal':
                strategyBadge = '<span class="badge bg-danger">Legal</span>';
                break;
            case 'Write-off':
                strategyBadge = '<span class="badge bg-secondary">Write-off</span>';
                break;
            default:
                strategyBadge = `<span class="badge bg-secondary">${account.collection_strategy || 'Unknown'}</span>`;
        }
        
        // Add cells
        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${account.customer_id || 'N/A'}</td>
            <td>${Math.round(account.priority_score || 0)}</td>
            <td>${strategyBadge}</td>
            <td>${formatCurrency(account.expected_recovery_value || 0)}</td>
            <td>${(account.recovery_roi || 0).toFixed(2)}</td>
            <td>${account.recommended_channel || 'N/A'}</td>
        `;
        
        resultsTableBody.appendChild(row);
    });
    
    // Scroll to results
    document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
}

function loadSampleData() {
    // Sample data for collections
    document.getElementById('customer_id').value = 'CUS000789';
    document.getElementById('days_past_due').value = '45';
    document.getElementById('outstanding_amount').value = '2500000';
    document.getElementById('number_of_contacts').value = '3';
    document.getElementById('previous_late_payments').value = '2';
    document.getElementById('promised_payment_amount').value = '500000';
    document.getElementById('broken_promises').value = '1';
    document.getElementById('months_on_book').value = '24';
    document.getElementById('last_payment_amount').value = '300000';
    
    // Add this sample to the table
    addAccountToTable();
    
    // Add a second sample
    document.getElementById('customer_id').value = 'CUS000790';
    document.getElementById('days_past_due').value = '60';
    document.getElementById('outstanding_amount').value = '3600000';
    document.getElementById('number_of_contacts').value = '5';
    document.getElementById('previous_late_payments').value = '3';
    document.getElementById('promised_payment_amount').value = '1000000';
    document.getElementById('broken_promises').value = '2';
    document.getElementById('months_on_book').value = '18';
    document.getElementById('last_payment_amount').value = '450000';
    
    // Add second sample to table
    addAccountToTable();
}

function formatCurrency(value) {
    return new Intl.NumberFormat('vi-VN', { 
        style: 'currency', 
        currency: 'VND',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}
