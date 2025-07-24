// CloudFront Function for redirecting to login page
function handler(event) {
    var request = event.request;
    var uri = request.uri;
    
    // Check if the request is for the root or doesn't have a file extension
    if (uri.endsWith('/') || !uri.includes('.')) {
        // If accessing root, redirect to login.html
        if (uri === '/' || uri === '') {
            request.uri = '/login.html';
        }
        // If accessing /index.html directly, allow it (auth check is in JS)
        else if (uri === '/index.html') {
            // Allow access, authentication will be checked by JavaScript
        }
        // For other paths without extension, try adding .html
        else if (!uri.endsWith('.html')) {
            request.uri = uri + '.html';
        }
    }
    
    return request;
}