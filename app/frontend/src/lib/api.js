const API_BASE = 'http://127.0.0.1:8000';

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
        const response = await fetch(`${API_BASE}/users/me/points`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            mode: 'cors',
            body: JSON.stringify({ points_to_add: pointsToAdd })  // ส่งเป็น JSON body
        });

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

// Create a review for a book
export async function createReview(bookId, rating, reviewText) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/books/${bookId}/reviews`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            rating: rating,
            review_text: reviewText
        })
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create review');
    }
    
    return response.json();
}

// Get all reviews for a book
export async function getBookReviews(bookId, skip = 0, limit = 20) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/books/${bookId}/reviews?skip=${skip}&limit=${limit}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get reviews');
    }
    
    return response.json();
}

// Update user's review
export async function updateReview(bookId, reviewId, rating = null, reviewText = null) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const body = {};
    if (rating !== null) body.rating = rating;
    if (reviewText !== null) body.review_text = reviewText;

    const response = await fetch(`${API_BASE}/books/${bookId}/reviews/${reviewId}`, {
        method: 'PATCH',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(body)
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to update review');
    }
    
    return response.json();
}

// Delete user's review
export async function deleteReview(bookId, reviewId) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/books/${bookId}/reviews/${reviewId}`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to delete review');
    }
    
    return response.json();
}

// Get all reviews by current user
export async function getUserReviews(skip = 0, limit = 20) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/books/user/reviews?skip=${skip}&limit=${limit}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get user reviews');
    }
    
    return response.json();
}

// Get creator dashboard statistics
export async function getCreatorStats() {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/creator/stats`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get creator stats');
    }
    
    return response.json();
}

// Get sales history (for chart)
export async function getSalesHistory(months = 6) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/creator/sales/history?months=${months}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get sales history');
    }
    
    return response.json();
}

// Get creator's books
export async function getCreatorBooks(skip = 0, limit = 20) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/creator/books?skip=${skip}&limit=${limit}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get creator books');
    }
    
    return response.json();
}

// Follow a creator
export async function followCreator(creatorUsername) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/creator/follow/${creatorUsername}`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to follow creator');
    }
    
    return response.json();
}

// Unfollow a creator
export async function unfollowCreator(creatorUsername) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/creator/unfollow/${creatorUsername}`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to unfollow creator');
    }
    
    return response.json();
}

// Update reading progress
export async function updateReadingProgress(bookId, progress) {
    const token = localStorage.getItem('token');
    if (!token) throw new Error('No token found');

    const response = await fetch(`${API_BASE}/books/reading/progress`, {
        method: 'PATCH',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            book_id: bookId,
            page: progress.page || 0,
            progress_percentage: progress.progress_percentage || 0,
            status: progress.status || 'reading'
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to update reading progress');
    }

    return response.json();
}

// Get books currently being read
export async function getReadingInProgress(skip = 0, limit = 10) {
    const token = localStorage.getItem('token');
    if (!token) throw new Error('No token found');

    const response = await fetch(`${API_BASE}/books/reading/in-progress?skip=${skip}&limit=${limit}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get in-progress books');
    }

    return response.json();
}

// Get completed books
export async function getReadingCompleted(skip = 0, limit = 10) {
    const token = localStorage.getItem('token');
    if (!token) throw new Error('No token found');

    const response = await fetch(`${API_BASE}/books/reading/completed?skip=${skip}&limit=${limit}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get completed books');
    }

    return response.json();
}

// Mark book as completed
export async function markBookCompleted(bookId) {
    const token = localStorage.getItem('token');
    if (!token) throw new Error('No token found');

    const formData = new FormData();
    formData.append('book_id', bookId);

    const response = await fetch(`${API_BASE}/books/reading/completed`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        body: formData
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to mark book as completed');
    }

    return response.json();
}

// Get reading statistics
export async function getReadingStats() {
    const token = localStorage.getItem('token');
    if (!token) throw new Error('No token found');

    const response = await fetch(`${API_BASE}/books/stats/reading`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get reading stats');
    }

    return response.json();
}

// ============ RECOMMENDATIONS ============

// Get personalized recommendations
export async function getPersonalizedRecommendations(limit = 10) {
    const token = localStorage.getItem('token');
    if (!token) throw new Error('No token found');

    const response = await fetch(`${API_BASE}/books/recommend/personalized?limit=${limit}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get personalized recommendations');
    }

    return response.json();
}

// Get category-based recommendations
export async function getCategoryRecommendations(category, limit = 10) {
    const token = localStorage.getItem('token');
    if (!token) throw new Error('No token found');

    const response = await fetch(`${API_BASE}/books/recommend/category/${encodeURIComponent(category)}?limit=${limit}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get category recommendations');
    }

    return response.json();
}

// ============ USER PROFILE UPDATE FUNCTIONS ============

// Get full user profile
export async function getUserProfile() {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/users/me/profile`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get profile');
    }
    
    return response.json();
}

// Update user profile information
export async function updateUserProfile(profileData) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    // Validate input
    const allowedFields = ['email', 'full_name', 'bio', 'avatar_url', 'country', 'phone'];
    const filteredData = {};
    
    for (const key of allowedFields) {
        if (profileData[key] !== undefined) {
            filteredData[key] = profileData[key];
        }
    }
    
    if (Object.keys(filteredData).length === 0) {
        throw new Error('No valid fields provided for update');
    }

    const response = await fetch(`${API_BASE}/users/me/profile`, {
        method: 'PATCH',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(filteredData)
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to update profile');
    }
    
    return response.json();
}

// Update specific profile fields
export async function updateProfileField(fieldName, fieldValue) {
    const allowedFields = ['email', 'full_name', 'bio', 'avatar_url', 'country', 'phone'];
    
    if (!allowedFields.includes(fieldName)) {
        throw new Error(`Invalid field: ${fieldName}`);
    }
    
    return updateUserProfile({ [fieldName]: fieldValue });
}

// Change username
export async function changeUsername(newUsername, currentPassword) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    // Validate new username
    if (!newUsername || newUsername.length < 3) {
        throw new Error('Username must be at least 3 characters');
    }
    
    if (newUsername.length > 30) {
        throw new Error('Username must not exceed 30 characters');
    }
    
    if (!/^[a-zA-Z0-9_]+$/.test(newUsername)) {
        throw new Error('Username can only contain letters, numbers, and underscores');
    }
    
    if (!currentPassword) {
        throw new Error('Current password is required');
    }

    const response = await fetch(`${API_BASE}/users/me/username`, {
        method: 'PATCH',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            new_username: newUsername,
            current_password: currentPassword
        })
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to change username');
    }
    
    return response.json();
}

// Get public user profile (limited information)
export async function getPublicUserProfile(username) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE}/users/profile/${encodeURIComponent(username)}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get user profile');
    }
    
    return response.json();
}

// ============ HELPER FUNCTIONS FOR PROFILE UPDATES ============

// Validate email format
export function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Validate username format
export function validateUsername(username) {
    if (username.length < 3 || username.length > 30) {
        return { valid: false, message: 'Username must be 3-30 characters' };
    }
    
    if (!/^[a-zA-Z0-9_]+$/.test(username)) {
        return { valid: false, message: 'Username can only contain letters, numbers, and underscores' };
    }
    
    return { valid: true, message: 'Username is valid' };
}

// Validate bio length
export function validateBio(bio) {
    if (bio.length > 500) {
        return { valid: false, message: 'Bio must not exceed 500 characters' };
    }
    
    return { valid: true, message: 'Bio is valid' };
}

// Validate phone format (optional - can be customized per region)
export function validatePhone(phone) {
    // Allow Thai phone format: +66 or 0, followed by 9 digits
    const phoneRegex = /^(\+66|0)\d{9}$/;
    return phoneRegex.test(phone.replace(/\s/g, ''));
}
