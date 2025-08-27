/**
 * Call the API via our Flask proxy
 * 
 * @param {string} endpoint - The API endpoint to call (without leading slash)
 * @param {string} method - HTTP method (GET or POST)
 * @param {object} data - The data to send (for POST requests)
 * @returns {Promise} - Promise resolving to the API response
 */
async function callApi(endpoint, method = 'GET', data = null) {
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
    
    try {
        const response = await fetch(url, options);
        
        if (!response.ok) {
            // Try to parse error message
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP error: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call error:', error);
        throw error;
    }
}
