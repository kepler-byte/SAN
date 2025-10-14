const API_BASE = 'https://san-yrrn.onrender.com';

export async function register(userData) {
    const response = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData)
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Registration failed');
    }
    
    return response.json();
}

export async function login(credentials) {
    const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials)
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
    }
    
    return response.json();
}

// Get payment history
export async function getPaymentHistory(limit = 20, skip = 0) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/users/me/payment/history?limit=${limit}&skip=${skip}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get payment history');
    }
    
    return response.json();
}

// Get current user info including points
export async function getCurrentUser() {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/users/me`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get user info');
    }
    
    return response.json();
}

// Add points
export async function addPoints(pointsToAdd) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/users/me/points?points_to_add=${pointsToAdd}`, {
        method: 'PATCH',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to add points');
    }
    
    return response.json();
}

// Process TrueMoney payment
export async function processTrueMoneyPayment(voucher, phone) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/users/me/payment/truemoney`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ voucher, phone })
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Payment failed');
    }
    
    return response.json();
}

// Get user settings
export async function getUserSettings() {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/users/me/settings`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get settings');
    }
    
    return response.json();
}

// Update user settings
export async function updateUserSettings(settings) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/users/me/settings`, {
        method: 'PATCH',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings)
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to update settings');
    }
    
    return response.json();
}

// Update specific setting
export async function updateSetting(key, value) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/users/me/settings/${key}`, {
        method: 'PATCH',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ value })
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to update setting');
    }
    
    return response.json();
}

// Upload a book (admin only) - Updated with category support
export async function uploadBook(bookData, coverFile = null) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const formData = new FormData();
    formData.append('title', bookData.title);
    formData.append('rating', bookData.rating);
    formData.append('description', bookData.description);
    formData.append('category', bookData.category || 'อื่นๆ');
    formData.append('price', bookData.price || 0);

    // Append cover file if provided
    if (coverFile) {
        formData.append('cover_file', coverFile);
    }

    const response = await fetch(`${API_BASE}/books/`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        body: formData
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to upload book');
    }
    
    return response.json();
}
// Get book details by ID
export async function getBookDetail(bookId) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/books/${bookId}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get book details');
    }
    
    return response.json();
}

// ✨ NEW: Get all available categories
export async function getBookCategories() {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/books/categories`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get categories');
    }
    
    return response.json();
}

// ✨ UPDATED: Get all books with enhanced filtering
export async function getAllBooks(skip = 0, limit = 10, options = {}) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    // Build query parameters
    const params = new URLSearchParams({
        skip: skip.toString(),
        limit: limit.toString()
    });

    if (options.category && options.category !== 'ทั้งหมด') {
        params.append('category', options.category);
    }

    if (options.search) {
        params.append('search', options.search);
    }

    if (options.sort_by) {
        params.append('sort_by', options.sort_by);
    }

    if (options.sort_order) {
        params.append('sort_order', options.sort_order.toString());
    }

    const response = await fetch(`${API_BASE}/books/?${params.toString()}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get books');
    }
    
    return response.json();
}

// ✨ NEW: Get books by specific category
export async function getBooksByCategory(category, skip = 0, limit = 20) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/books/category/${encodeURIComponent(category)}?skip=${skip}&limit=${limit}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get books by category');
    }
    
    return response.json();
}

// ✨ NEW: Get category statistics
export async function getCategoryStats() {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/books/stats/categories`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get category stats');
    }
    
    return response.json();
}

// ✨ DEPRECATED: Use getAllBooks with options instead
export async function searchBooks(query = '', skip = 0, limit = 20) {
    return getAllBooks(skip, limit, { search: query });
}