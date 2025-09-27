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

    // Validate points
    if (!pointsToAdd || pointsToAdd <= 0) {
        throw new Error('Points must be greater than 0');
    }

    try {
        const response = await fetch(`${API_BASE}/users/me/points?points_to_add=${pointsToAdd}`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            // เพิ่ม mode สำหรับ CORS
            mode: 'cors',
        });

        // Check if response is ok
        if (!response.ok) {
            let errorMessage = `HTTP ${response.status}`;
            
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorMessage;
            } catch (jsonError) {
                console.warn('Could not parse error response as JSON');
            }
            
            throw new Error(errorMessage);
        }

        const result = await response.json();
        return result;
        
    } catch (error) {
        // Handle different types of errors
        if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
            throw new Error('Cannot connect to server. Please check if the backend is running.');
        } else if (error.name === 'SyntaxError') {
            throw new Error('Server returned invalid response. Please try again.');
        } else {
            throw error;
        }
    }
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

// 🆕 UPDATED: Upload a book with PDF support (admin only)
export async function uploadBook(bookData, coverFile = null, pdfFile = null) {
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

    // 🆕 NEW: Append PDF file if provided
    if (pdfFile) {
        formData.append('pdf_file', pdfFile);
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

// 🆕 NEW: Get book cover image from GridFS
export async function getBookCover(bookId) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/books/${bookId}/cover`, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
    });
    
    if (!response.ok) {
        if (response.status === 404) {
            return null; // No cover available
        }
        const error = await response.json().catch(() => ({ detail: 'Failed to get cover' }));
        throw new Error(error.detail || 'Failed to get book cover');
    }
    
    return response.blob(); // Return image blob
}

// Helper function to create object URL from book ID
export async function getBookCoverObjectUrl(bookId) {
    try {
        const blob = await getBookCover(bookId);
        if (!blob) return null;
        return URL.createObjectURL(blob);
    } catch (error) {
        console.error('Failed to get cover URL:', error);
        return null;
    }
}

// 🆕 NEW: Get book cover URL (for img src)
export function getBookCoverUrl(bookId) {
    const token = localStorage.getItem('token');
    return `${API_BASE}/books/${bookId}/cover?token=${encodeURIComponent(token)}`;
}

// 🆕 NEW: Read book (stream PDF)
export async function readBook(bookId) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/books/${bookId}/read`, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
    });
    
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Failed to read book' }));
        throw new Error(error.detail || 'Failed to read book');
    }
    
    return response.blob(); // Return PDF blob
}

// 🆕 NEW: Get PDF URL for embedding (for iframe src)
export function getBookReadUrl(bookId) {
    const token = localStorage.getItem('token');
    return `${API_BASE}/books/${bookId}/read?token=${encodeURIComponent(token)}`;
}

// 🆕 NEW: Download book PDF
export async function downloadBook(bookId) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/books/${bookId}/download`, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
    });
    
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Failed to download book' }));
        throw new Error(error.detail || 'Failed to download book');
    }
    
    // Get filename from response headers
    const contentDisposition = response.headers.get('Content-Disposition');
    let filename = 'book.pdf';
    if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="([^"]+)"/);
        if (filenameMatch) {
            filename = filenameMatch[1];
        }
    }
    
    const blob = await response.blob();
    
    // Create download link
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    return { success: true, filename };
}

// 🆕 NEW: Delete book (admin only)
export async function deleteBook(bookId) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/books/${bookId}`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to delete book');
    }
    
    return response.json();
}

// Get all available categories
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

// Get all books with enhanced filtering
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

// Get books by specific category
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

// Get category statistics
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

// 🆕 NEW: Get storage statistics (admin only)
export async function getStorageStats() {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/books/stats/storage`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get storage stats');
    }
    
    return response.json();
}

// DEPRECATED: Use getAllBooks with options instead
export async function searchBooks(query = '', skip = 0, limit = 20) {
    return getAllBooks(skip, limit, { search: query });
}

// Purchase a book with points
export async function purchaseBook(bookId) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/users/me/purchase/book`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ book_id: bookId })
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to purchase book');
    }
    
    return response.json();
}

// Get user's library (purchased books)
export async function getUserLibrary(skip = 0, limit = 20) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/users/me/library?skip=${skip}&limit=${limit}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get library');
    }
    
    return response.json();
}

// Check if user owns a specific book
export async function checkBookOwnership(bookId) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/users/me/library/check/${bookId}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to check ownership');
    }
    
    return response.json();
}

// Get user statistics
export async function getUserStats() {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/users/me/stats`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get user stats');
    }
    
    return response.json();
}

// Remove book from library
export async function removeBookFromLibrary(bookId) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/users/me/library/${bookId}`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to remove book');
    }
    
    return response.json();
}