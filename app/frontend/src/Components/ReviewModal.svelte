<script>
  import { createEventDispatcher } from 'svelte';
  import { X, Star } from '@lucide/svelte';
  import { getBookReviews, createReview, updateReview, deleteReview } from '../lib/api.js';
  
  export let bookId = '';
  export let bookTitle = '';
  export let userOwnsBook = false;
  export let bookIsFree = false;
  
  const dispatch = createEventDispatcher();
  
  let reviews = [];
  let totalReviews = 0;
  let averageRating = 0;
  let loading = true;
  let showWriteReview = false;
  let userReview = null;
  
  // Write review form
  let newRating = 5;
  let newReviewText = '';
  let submitting = false;
  
  // Edit review
  let editingReview = null;
  
  async function loadReviews() {
    try {
      loading = true;
      const data = await getBookReviews(bookId, 0, 50);
      reviews = data.reviews;
      totalReviews = data.total_reviews;
      averageRating = data.average_rating;
      
      // Find user's review if exists
      userReview = reviews.find(r => r.is_owner) || null;
      
    } catch (error) {
      console.error('Failed to load reviews:', error);
    } finally {
      loading = false;
    }
  }
  
  async function handleSubmitReview() {
    if (newReviewText.length < 10) {
      alert('รีวิวต้องมีอย่างน้อย 10 ตัวอักษร');
      return;
    }
    
    try {
      submitting = true;
      
      if (editingReview) {
        // Update existing review
        await updateReview(bookId, editingReview.review_id, newRating, newReviewText);
      } else {
        // Create new review
        await createReview(bookId, newRating, newReviewText);
      }
      
      // Reset form
      showWriteReview = false;
      editingReview = null;
      newRating = 5;
      newReviewText = '';
      
      // Reload reviews
      await loadReviews();
      
    } catch (error) {
      alert('ไม่สามารถบันทึกรีวิวได้: ' + error.message);
    } finally {
      submitting = false;
    }
  }
  
  async function handleDeleteReview(reviewId) {
    if (!confirm('ต้องการลบรีวิวนี้หรือไม่?')) {
      return;
    }
    
    try {
      await deleteReview(bookId, reviewId);
      await loadReviews();
    } catch (error) {
      alert('ไม่สามารถลบรีวิวได้: ' + error.message);
    }
  }
  
  function startEditReview(review) {
    editingReview = review;
    newRating = review.rating;
    newReviewText = review.review_text;
    showWriteReview = true;
  }
  
  function cancelWriteReview() {
    showWriteReview = false;
    editingReview = null;
    newRating = 5;
    newReviewText = '';
  }
  
  function close() {
    dispatch('close');
  }
  
  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('th-TH', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
  
  // Load reviews on mount
  $: if (bookId) {
    loadReviews();
  }
  
  // Check if user can write review
  $: canWriteReview = (userOwnsBook || bookIsFree) && !userReview;
</script>

<div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" on:click|self={close}>
  <div class="bg-white rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden m-4">
    <!-- Header -->
    <div class="flex items-center justify-between p-6 border-b border-gray-200">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">รีวิวหนังสือ</h2>
        <p class="text-sm text-gray-600 mt-1">{bookTitle}</p>
      </div>
      <button
        on:click={close}
        class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full transition-colors"
      >
        <X class="w-6 h-6" />
      </button>
    </div>
    
    <!-- Content -->
    <div class="overflow-y-auto max-h-[calc(90vh-120px)] p-6">
      {#if loading}
        <!-- Loading State -->
        <div class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-400"></div>
        </div>
      {:else}
        <!-- Summary -->
        <div class="bg-gradient-to-r from-orange-50 to-orange-100 rounded-lg p-6 mb-6">
          <div class="flex items-center justify-between">
            <div>
              <div class="flex items-center gap-2 mb-2">
                <span class="text-4xl font-bold text-gray-900">{averageRating.toFixed(1)}</span>
                <Star class="w-8 h-8 text-yellow-500 fill-yellow-500" />
              </div>
              <p class="text-sm text-gray-600">{totalReviews} รีวิว</p>
            </div>
            
            {#if canWriteReview}
              <button
                on:click={() => showWriteReview = true}
                class="bg-orange-500 hover:bg-orange-600 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
              >
                เขียนรีวิว
              </button>
            {/if}
          </div>
        </div>
        
        <!-- Write/Edit Review Form -->
        {#if showWriteReview}
          <div class="bg-gray-50 rounded-lg p-6 mb-6 border-2 border-orange-200">
            <h3 class="text-lg font-semibold mb-4">
              {editingReview ? 'แก้ไขรีวิว' : 'เขียนรีวิวของคุณ'}
            </h3>
            
            <!-- Rating -->
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">คะแนน</label>
              <div class="flex gap-2">
                {#each [1, 2, 3, 4, 5] as star}
                  <button
                    on:click={() => newRating = star}
                    class="transition-transform hover:scale-110"
                  >
                    <Star 
                      class={`w-8 h-8 ${star <= newRating ? 'text-yellow-500 fill-yellow-500' : 'text-gray-300'}`}
                    />
                  </button>
                {/each}
              </div>
            </div>
            
            <!-- Review Text -->
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">รีวิว (ขั้นต่ำ 10 ตัวอักษร)</label>
              <textarea
                bind:value={newReviewText}
                rows="5"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent resize-none"
                placeholder="เขียนรีวิวของคุณที่นี่..."
              ></textarea>
              <p class="text-xs text-gray-500 mt-1">{newReviewText.length} / 2000 ตัวอักษร</p>
            </div>
            
            <!-- Buttons -->
            <div class="flex gap-3">
              <button
                on:click={handleSubmitReview}
                disabled={submitting || newReviewText.length < 10}
                class="flex-1 bg-orange-500 hover:bg-orange-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg font-semibold transition-colors"
              >
                {submitting ? 'กำลังบันทึก...' : editingReview ? 'บันทึกการแก้ไข' : 'ส่งรีวิว'}
              </button>
              <button
                on:click={cancelWriteReview}
                disabled={submitting}
                class="px-6 py-3 border border-gray-300 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
              >
                ยกเลิก
              </button>
            </div>
          </div>
        {/if}
        
        <!-- Reviews List -->
        <div class="space-y-4">
          <h3 class="text-lg font-semibold mb-4">รีวิวทั้งหมด</h3>
          
          {#if reviews.length === 0}
            <div class="text-center py-12">
              <p class="text-gray-500">ยังไม่มีรีวิวสำหรับหนังสือเล่มนี้</p>
              {#if canWriteReview}
                <p class="text-sm text-gray-400 mt-2">เป็นคนแรกที่เขียนรีวิว!</p>
              {/if}
            </div>
          {:else}
            {#each reviews as review}
              <div class="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                <!-- Review Header -->
                <div class="flex items-start justify-between mb-3">
                  <div class="flex-1">
                    <div class="flex items-center gap-2 mb-1">
                      <span class="font-semibold text-gray-900">{review.username}</span>
                      {#if review.is_owner}
                        <span class="bg-orange-100 text-orange-700 text-xs px-2 py-1 rounded">รีวิวของคุณ</span>
                      {/if}
                    </div>
                    <p class="text-xs text-gray-500">{formatDate(review.created_at)}</p>
                  </div>
                  
                  <!-- Actions for own review -->
                  {#if review.is_owner}
                    <div class="flex gap-2">
                      <button
                        on:click={() => startEditReview(review)}
                        class="text-sm text-blue-600 hover:text-blue-800 font-medium"
                      >
                        แก้ไข
                      </button>
                      <button
                        on:click={() => handleDeleteReview(review.review_id)}
                        class="text-sm text-red-600 hover:text-red-800 font-medium"
                      >
                        ลบ
                      </button>
                    </div>
                  {/if}
                </div>
                
                <!-- Rating -->
                <div class="flex gap-1 mb-3">
                  {#each [1, 2, 3, 4, 5] as star}
                    <Star 
                      class={`w-5 h-5 ${star <= review.rating ? 'text-yellow-500 fill-yellow-500' : 'text-gray-300'}`}
                    />
                  {/each}
                  <span class="text-sm text-gray-600 ml-2">{review.rating}/5</span>
                </div>
                
                <!-- Review Text -->
                <p class="text-gray-700 leading-relaxed whitespace-pre-line">{review.review_text}</p>
                
                <!-- Updated indicator -->
                {#if review.updated_at !== review.created_at}
                  <p class="text-xs text-gray-400 mt-3">แก้ไขเมื่อ {formatDate(review.updated_at)}</p>
                {/if}
              </div>
            {/each}
          {/if}
        </div>
        
        <!-- Message for users who can't review -->
        {#if !canWriteReview && !userReview && totalReviews > 0}
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-6">
            <p class="text-sm text-blue-800">
              💡 คุณต้องซื้อหนังสือก่อนจึงจะสามารถเขียนรีวิวได้
            </p>
          </div>
        {/if}
      {/if}
    </div>
  </div>
</div>

<style>
  /* Custom scrollbar */
  .overflow-y-auto::-webkit-scrollbar {
    width: 8px;
  }
  
  .overflow-y-auto::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 10px;
  }
  
  .overflow-y-auto::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 10px;
  }
  
  .overflow-y-auto::-webkit-scrollbar-thumb:hover {
    background: #555;
  }
</style>