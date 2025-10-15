<script>
  import { onMount, createEventDispatcher, onDestroy } from 'svelte';
  import SANPoint from "../assets/SAN_Point_White.svg";
  import { Book, Bookmark, CircleArrowLeft, X, Download, Star } from '@lucide/svelte';
  // 1. Import the 'updateReadingProgress' function
  import { 
    getBookCover, 
    readBook, 
    purchaseBook, 
    checkBookOwnership, 
    getCurrentUser, 
    getBookReviews,
    updateReadingProgress // 👈 ADD THIS IMPORT
  } from '../lib/api.js';
  import { authToken, currentUser } from '../lib/auth.js';
  import ReviewModal from '../components/ReviewModal.svelte';
  import CreatorPopover from '../components/CreatorPopover.svelte';

  
  const dispatch = createEventDispatcher();

  let isBookmarked = false;
  let showDescription = false;
  let showPdfModal = false;
  let pdfUrl = '';
  let loadingPdf = false;
  let purchasingBook = false;
  let userOwnsBook = false;
  let showCreatorPopover = false;
  let userPoints = 0;
  let isInitialLoading = true; 
  let showReviewModal = false;
  let reviewCount = 0;
  let averageRating = 0;
  
  let bookData = {
    title: "The Book is unavailable",
    author: "unknown", 
    rating: 5,
    price: 0,
    description: "Internal error: Book data not found.",
    cover: "",
    id: "",
    has_pdf: false,
    has_cover: false
  };
  let coverImageUrl = "";
  let loadingCover = true;
  let coverObjectUrls = [];
  $: if ($currentUser) {
    userPoints = $currentUser.points || 0;
  }

  onDestroy(() => {
    // Cleanup
    coverObjectUrls.forEach(url => {
      URL.revokeObjectURL(url);
    });
    if (pdfUrl) {
      URL.revokeObjectURL(pdfUrl);
    }
    
    // Remove event listener
    window.removeEventListener('focus', handleWindowFocus);
  });
  async function loadCoverImage() {
    try {
      loadingCover = true;
      const blob = await getBookCover(bookData.id);
      if (blob) {
        const objectUrl = URL.createObjectURL(blob);
        coverImageUrl = objectUrl;
        coverObjectUrls.push(objectUrl);
      }
    } catch (error) {
      console.error('Failed to load cover image:', error);
    } finally {
      loadingCover = false;
    }
  }

  async function refreshUserData() {
    try {
      const userData = await getCurrentUser();
      currentUser.set(userData);
      userPoints = userData.points || 0;
      
      const ownershipCheck = await checkBookOwnership(bookData.id);
      userOwnsBook = ownershipCheck.owned;
      // โหลดจำนวนรีวิว
      try {
        const reviewData = await getBookReviews(bookData.id, 0, 1);
        reviewCount = reviewData.total_reviews;
        averageRating = reviewData.average_rating || 0;
      } catch (error) {
        console.error('Failed to load review count:', error);
        reviewCount = 0;
        averageRating = 0;
      }
      
      console.log('User data refreshed:', { points: userPoints, owns: userOwnsBook, reviews: reviewCount, rating: averageRating });
    } catch (error) {
      console.error('Failed to refresh user data:', error);
    }
  }

  function handleWindowFocus() {
    console.log('Window focused - refreshing user data');
    refreshUserData();
  }

  onMount(async () => {
    isInitialLoading = true;
    
    try {
      // Get book data from sessionStorage
      const selectedBook = sessionStorage.getItem('selectedBook');
      if (selectedBook) {
        const parsedBook = JSON.parse(selectedBook);
        bookData = {
          ...bookData,
          ...parsedBook,
          price: 
            parsedBook.price ?? 0
        };
        
        // Load cover image and user data in parallel
        await Promise.all([
          bookData.has_cover && bookData.id ? loadCoverImage() : Promise.resolve(),
          refreshUserData()
        ]);
        
        if (!bookData.has_cover) {
     
           loadingCover = false;
        }
      }
      
      // Add event listener for window focus
      window.addEventListener('focus', handleWindowFocus);
      
      console.log('Book data loaded:', bookData);
    } catch (error) {
      console.error('Error loading book data:', error);
    } finally {
      isInitialLoading = false;
    }
  });
  function goBack() {
    dispatch('navigate', 'home');
  }
  
  function toggleBookmark() {
    isBookmarked = !isBookmarked;
  }
  
  async function handlePreview() {
    console.log('Preview clicked for book:', bookData.id);
    if (!bookData.has_pdf) {
      alert('PDF ไม่พร้อมใช้งานสำหรับหนังสือเล่มนี้');
      return;
    }
    
    // Check if user owns the book or if it's free
    if (bookData.price > 0 && !userOwnsBook) {
      alert('คุณต้องซื้อหนังสือก่อนจึงจะสามารถอ่านได้');
      return;
    }
    
    try {
      loadingPdf = true;
      const pdfBlob = await readBook(bookData.id);

      // 2. Add the progress update logic here
      try {
        // This notifies the backend that the user has started reading.
        // We send a simple progress object; this could be expanded later.
        await updateReadingProgress(bookData.id, { page: 1 }); // 👈 ADD THIS BLOCK
        console.log(`Reading progress updated for book: ${bookData.id}`);
      } catch (progressError) {
        // It's not critical to inform the user if this fails, as it's a background task.
        console.error('Could not update reading progress:', progressError);
      }
      
      // Clean up previous PDF URL if exists
      if (pdfUrl) {
        URL.revokeObjectURL(pdfUrl);
      }
      
      pdfUrl = URL.createObjectURL(pdfBlob);
      showPdfModal = true;
    } catch (error) {
      console.error('Failed to open PDF:', error);
      alert('ไม่สามารถเปิด PDF ได้: ' + error.message);
    } finally {
      loadingPdf = false;
    }
  }

  function closePdfModal() {
    showPdfModal = false;
    if (pdfUrl) {
      setTimeout(() => {
        URL.revokeObjectURL(pdfUrl);
        pdfUrl = '';
      }, 300);
    }
  }

  // Handle escape key to close modal
  function handleKeydown(event) {
    if (event.key === 'Escape' && showPdfModal) {
      closePdfModal();
    }
  }

  async function downloadPdf() {
    if (!pdfUrl) return;
    try {
      const link = document.createElement('a');
      link.href = pdfUrl;
      link.download = `${bookData.title}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Failed to download PDF:', error);
    }
  }
  
  function handleReview() {
    showReviewModal = true;
  }
  
  async function handlePurchase() {
    console.log('Purchase clicked for price:', bookData.price);
    if (bookData.price === 0) {
      console.log('Free book - proceeding to read');
      await handlePreview();
      return;
    }
    
    // Check if user already owns the book
    if (userOwnsBook) {
      console.log('User already owns this book - proceeding to read');
      await handlePreview();
      return;
    }
    
    // Check if user has enough points
    if (userPoints < bookData.price) {
      alert(`คุณมี Points ไม่พอ!\nคุณมี: ${userPoints} Points\nต้องการ: ${bookData.price} Points\nกรุณาเติม Points เพิ่ม`);
      return;
    }
    
    // Confirm purchase
    const confirmPurchase = confirm(
      `ต้องการซื้อหนังสือ "${bookData.title}" ในราคา ${bookData.price} Points หรือไม่?\n\nPoints ที่มี: ${userPoints}\nPoints หลังซื้อ: ${userPoints - bookData.price}`
    );
    if (!confirmPurchase) {
      return;
    }
    
    try {
      purchasingBook = true;
      const purchaseResult = await purchaseBook(bookData.id);
      
      // Update user state
      userOwnsBook = true;
      userPoints = purchaseResult.purchase_details.remaining_points;
      // Show success message
      alert(`🎉 ซื้อสำเร็จ!\n\n"${bookData.title}"\nราคา: ${bookData.price} Points\nPoints ที่เหลือ: ${userPoints}\n\nตอนนี้คุณสามารถอ่านหนังสือได้แล้ว!`);
      // Automatically open the book for reading
      await handlePreview();
    } catch (error) {
      console.error('Purchase failed:', error);
      alert(`ไม่สามารถซื้อหนังสือได้: ${error.message}`);
    } finally {
      purchasingBook = false;
    }
  }

  function formatPrice(price) {
    if (price === undefined || price === null || price === 0) {
      return 'ฟรี';
    }
    return price.toString();
  }

  $: displayPrice = bookData.price ?? 0;
  $: priceText = displayPrice === 0 ? 'ฟรี' : displayPrice.toString();
  function handleCoverError(event) {
    console.log('Cover image failed to load');
    event.target.style.display = 'none';
  }
</script>

<svelte:window on:keydown={handleKeydown} />
<CreatorPopover 
     bind:isOpen={showCreatorPopover}
     creatorUsername={bookData.author}
     onClose={() => showCreatorPopover = false}
   />
   
<div class="min-h-screen bg-white relative">
  <!-- Loading Screen -->
  {#if isInitialLoading}
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-white">
      <div class="text-center">
        <div class="relative w-20 h-20 mx-auto mb-6">
          <div class="absolute inset-0 rounded-full border-4 border-orange-100"></div>
          <div class="absolute inset-0 rounded-full border-4 border-orange-500 border-t-transparent animate-spin"></div>
          <div class="absolute inset-2 flex items-center justify-center">
            <Book class="w-8 h-8 text-orange-500" />
          </div>
        </div>
        <h3 class="text-xl font-semibold text-gray-800 mb-2">กำลังโหลดข้อมูล</h3>
        <p class="text-sm text-gray-500">กรุณารอสักครู่...</p>
      </div>
    </div>
  {:else}
    <!-- Mobile Layout -->
    <div class="lg:hidden w-full mx-auto relative overflow-hidden">
      <!-- Header -->
      <div class="flex justify-between items-center p-6">
        <button class="w-6 h-6 flex items-center justify-center" on:click={goBack}>
          <CircleArrowLeft class="w-6 h-6 text-gray-600" />
        </button>
        
        <div class="flex gap-3">
          <!-- User Points Display -->
          <div class="flex items-center gap-1 bg-orange-100 px-2 py-1 rounded-full">
            <img src={SANPoint} alt="SAN Logo" class="w-3 h-3 object-contain" />
            <span class="text-xs font-bold text-orange-600">{userPoints}</span>
          </div>
          
          <button 
            class="w-6 h-6 flex items-center justify-center"
            on:click={toggleBookmark}
            class:text-red-500={isBookmarked}
          >
            <Bookmark fill={isBookmarked ? "currentColor" : "none"} stroke="currentColor" class="w-6 h-6" />
          </button>
        </div>
      </div>

      <!-- Book Cover -->
      <div class="flex justify-center px-6 mb-8">
        <div class="relative">
          <div class="w-2.5 h-80 absolute left-0 top-0 bg-stone-500 z-10"></div>
          <div class="w-52 h-80 bg-gradient-to-r from-stone-500 to-stone-700 rounded-r-md shadow-2xl relative overflow-hidden">
            {#if loadingCover}
              <div class="absolute inset-0 flex items-center justify-center bg-gray-200">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-400"></div>
              </div>
            {:else if coverImageUrl && bookData.has_cover}
              <img 
                src={coverImageUrl} 
                alt={bookData.title} 
                class="w-full h-full object-cover"
                on:error={handleCoverError}
              />
            {:else}
              <div class="absolute inset-0 flex flex-col items-center justify-center text-black px-8">
                <h1 class="text-xl font-bold text-center mb-2">IMAGE BOOK COVER</h1>
                <p class="text-sm font-light italic text-center mb-8">CAN NOT BE LOAD</p>
                {#if !bookData.has_cover}
                  <p class="text-xs text-center text-gray-600">ไม่มีรูปปก</p>
                {/if}
              </div>
            {/if}
          </div>
          <div class="w-[1px] h-80 absolute left-2.5 top-0 bg-stone-700 z-10"></div>
        </div>
      </div>

      <!-- Book Info -->
      <div class="px-6 text-center mb-8">
        <h2 class="text-2xl font-semibold text-zinc-950 mb-2">{bookData.title}</h2>
        <p 
     class="text-xs text-zinc-500 mb-4 cursor-pointer hover:text-orange-500"
     on:click={() => showCreatorPopover = true}
   >
     แต่งโดย {bookData.author}
   </p>
        
        <div class="flex items-center justify-center gap-1 mb-4">
          <div class="flex text-yellow-400">
            {#each Array(5) as _, i}
              <span class={i < Math.floor(averageRating || bookData.rating) ? "text-yellow-400" : "text-gray-300"}><Star /></span>
            {/each}
          </div>
          <span class="text-sm font-medium text-zinc-950 ml-2">{averageRating || bookData.rating}</span>
          <span class="text-sm text-zinc-500">/ 5.0</span>
          {#if reviewCount > 0}
            <span class="text-xs text-gray-400 ml-1">({reviewCount} รีวิว)</span>
          {/if}
        </div>
        
        <!-- PDF Status Indicator -->
        <div class="flex items-center justify-center mb-4">
          {#if bookData.has_pdf}
            <div class="flex items-center gap-2 text-green-600 text-sm">
              <Book class="w-4 h-4" />
              <span>PDF พร้อมอ่าน</span>
            </div>
          {:else}
            <div class="flex items-center gap-2 text-gray-500 text-sm">
              <Book class="w-4 h-4" />
              <span>PDF ไม่พร้อมใช้งาน</span>
            </div>
          {/if}
        </div>
        
        <p class="text-sm text-zinc-500 opacity-50 leading-normal mb-8">
          {bookData.description}
        </p>
      </div>

      <!-- Action Buttons -->
      <div class="px-6 mb-8">
        <div class="flex gap-4 mb-4">
          <button 
            class="flex-1 bg-white rounded-lg shadow-md px-4 py-3 flex items-center justify-center gap-2 hover:shadow-lg transition-shadow relative"
            class:opacity-50={!bookData.has_pdf || loadingPdf || (bookData.price > 0 && !userOwnsBook)}
            class:cursor-not-allowed={!bookData.has_pdf || loadingPdf || (bookData.price > 0 && !userOwnsBook)}
            on:click={handlePreview}
            disabled={!bookData.has_pdf || loadingPdf || (bookData.price > 0 && !userOwnsBook)}
          >
            {#if loadingPdf}
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-orange-400"></div>
            {:else}
              <svg class="w-4 h-3" fill="currentColor" viewBox="0 0 16 12">
                <path d="M8 0C4.5 0 1.6 2.4 0 6c1.6 3.6 4.5 6 8 6s6.4-2.4 8-6c-1.6-3.6-4.5-6-8-6zm0 10c-2.2 0-4-1.8-4-4s1.8-4 4-4 4 1.8 4 4-1.8 4-4 4z"/>
                <circle cx="8" cy="6" r="2"/>
              </svg>
            {/if}
            <span class="text-sm font-bold text-zinc-950">
              {loadingPdf ? 'กำลังโหลด...' : 
               (bookData.price > 0 && !userOwnsBook) ? 'ต้องซื้อก่อน' : 'ดูตัวอย่าง'}
            </span>
          </button>
          
          <button 
            class="flex-1 bg-white rounded-lg shadow-md px-4 py-3 flex items-center justify-center gap-2 hover:shadow-lg transition-shadow"
            on:click={handleReview}
          >
            <svg class="w-5 h-4" fill="currentColor" viewBox="0 0 20 16">
              <path d="M18 0H2C0.9 0 0 0.9 0 2v12c0 1.1 0.9 2 2 2h16c1.1 0 2-0.9 2-2V2c0-1.1-0.9-2-2-2zM6 4h8v2H6V4zm8 6H6V8h8v2zm2-8v12H4V2h12z"/>
            </svg>
            <span class="text-sm font-bold text-zinc-950">รีวิว</span>
          </button>
        </div>
        
        <button 
          class="w-full rounded-[20px] shadow-lg px-28 py-4 flex items-center justify-center gap-2.5 transition-colors relative"
          class:bg-zinc-950={displayPrice > 0 && !userOwnsBook}
          class:bg-green-600={displayPrice === 0 || userOwnsBook}
          class:hover:bg-zinc-800={displayPrice > 0 && !userOwnsBook}
          class:hover:bg-green-700={displayPrice === 0 || userOwnsBook}
          class:opacity-50={purchasingBook}
          class:cursor-not-allowed={purchasingBook}
          on:click={handlePurchase}
          disabled={purchasingBook}
        >
          {#if purchasingBook}
            <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            <span class="text-white text-base font-bold">กำลังซื้อ...</span>
          {:else}
            <span class="text-white text-base font-bold">
              {userOwnsBook ? 'เปิดอ่าน' : 
               displayPrice === 0 ? 'อ่านฟรี' : 
               userPoints < displayPrice ? `ต้องการ ${displayPrice - userPoints} Points` : 'ซื้อเล่มนี้'}
            </span>
            <div class="rounded-full px-2 py-1 flex items-center gap-1"
                 class:bg-orange-400={displayPrice > 0 && !userOwnsBook}
                 class:bg-green-500={displayPrice === 0 || userOwnsBook}>
              <img src={SANPoint} alt="SAN Logo" class="w-4 h-4 object-contain" />
              <span class="text-white text-xs font-bold">
                {userOwnsBook ? 'เป็นเจ้าของแล้ว' : priceText}
              </span>
            </div>
          {/if}
        </button>
      </div>
    </div>

    <!-- Desktop Layout -->
    <div class="hidden lg:flex min-h-screen">
      <!-- Left Side - Book Cover -->
      <div class="w-1/2 flex flex-col justify-center items-center bg-gradient-to-br from-gray-50 to-gray-100 p-16">
        <div class="relative max-w-md">
          <div class="w-4 h-96 absolute left-0 top-0 bg-stone-500 z-10 rounded-l-lg"></div>
          <div class="w-80 h-96 bg-gradient-to-r from-stone-500 to-stone-700 rounded-r-xl shadow-2xl relative overflow-hidden">
            {#if loadingCover}
              <div class="absolute inset-0 flex items-center justify-center bg-gray-200">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-400"></div>
              </div>
            {:else if coverImageUrl && bookData.has_cover}
              <img 
                src={coverImageUrl} 
                alt={bookData.title} 
                class="w-full h-full object-cover"
                on:error={handleCoverError}
              />
            {:else}
              <div class="absolute inset-0 flex flex-col items-center justify-center text-black px-12">
                <h1 class="text-3xl font-bold text-center mb-4">{bookData.title.toUpperCase()}</h1>
<p 
     class="text-xs text-zinc-500 mb-4 cursor-pointer hover:text-orange-500"
     on:click={() => showCreatorPopover = true}
   >
     แต่งโดย {bookData.author}
   </p>                <p class="text-2xl font-semibold text-center">หนังสือ</p>
              </div>
            {/if}
          </div>
          <div class="w-[2px] h-96 absolute left-4 top-0 bg-stone-700 z-10"></div>
        </div>
      </div>

      <!-- Right Side - Content -->
      <div class="w-1/2 flex flex-col justify-center px-16 py-16">
        <!-- Header -->
        <div class="flex justify-between items-start mb-12">
          <button 
            class="w-8 h-8 flex items-center justify-center text-gray-600 hover:text-gray-900"
            on:click={goBack}
          >
            <CircleArrowLeft />
          </button>
          
          <div class="flex gap-4">
            <!-- User Points Display Desktop -->
            <div class="flex items-center gap-2 bg-orange-100 px-3 py-2 rounded-full">
              <img src={SANPoint} alt="SAN Logo" class="w-4 h-4 object-contain" />
              <span class="text-sm font-bold text-orange-600">{userPoints} Points</span>
            </div>
            
            <button 
              class="w-8 h-8 flex items-center justify-center text-gray-600 hover:text-gray-900"
              on:click={toggleBookmark}
              class:text-red-500={isBookmarked}
            >
              <Bookmark fill={isBookmarked ? "currentColor" : "none"} stroke="currentColor" class="w-10 h-10" />
            </button>
          </div>
        </div>

        <!-- Book Info -->
        <div class="mb-12">
          <h1 class="text-5xl font-bold text-zinc-950 mb-4">{bookData.title}</h1>
<p 
     class="text-xs text-zinc-500 mb-4 cursor-pointer hover:text-orange-500"
     on:click={() => showCreatorPopover = true}
   >
     แต่งโดย {bookData.author}
   </p>          
          <div class="flex items-center gap-2 mb-6">
            <div class="flex text-yellow-400 text-xl">
              {#each Array(5) as _, i}
                <span class={i < Math.floor(bookData.rating) ? "text-yellow-400" : "text-gray-300"}>⭐</span>
              {/each}
            </div>
            <span class="text-xl font-medium text-zinc-950 ml-2">{bookData.rating}</span>
            <span class="text-xl text-zinc-500">/ 5.0</span>
          </div>

          <!-- PDF Status Indicator Desktop -->
          <div class="flex items-center mb-6">
            {#if bookData.has_pdf}
              <div class="flex items-center gap-3 text-green-600 text-lg">
                <Book class="w-5 h-5" />
                <span>PDF พร้อมอ่าน</span>
              </div>
            {:else}
              <div class="flex items-center gap-3 text-gray-500 text-lg">
                <Book class="w-5 h-5" />
                <span>PDF ไม่พร้อมใช้งาน</span>
              </div>
            {/if}
          </div>

          <!-- Description -->
          <div class="border border-zinc-300 rounded-lg p-4 bg-white shadow-sm mb-12 w-full">
            <div class="flex justify-between items-center cursor-pointer" on:click={() => showDescription = !showDescription}>
              <h3 class="text-lg font-medium text-zinc-800">รายละเอียดหนังสือ</h3>
              <svg 
                class={`w-5 h-5 text-zinc-500 transition-transform ${showDescription ? 'rotate-180' : ''}`} 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>

            {#if showDescription}
              <div class="mt-4 pt-4 border-t border-zinc-200">
                <p class="text-base text-zinc-600 leading-relaxed whitespace-pre-line">
                  {bookData.description}
                </p>
              </div>
            {/if}
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="space-y-6">
          <div class="flex gap-6">
            <button 
              class="flex-1 bg-white rounded-xl shadow-lg px-6 py-4 flex items-center justify-center gap-3 hover:shadow-xl transition-shadow relative"
              class:opacity-50={!bookData.has_pdf || loadingPdf || (bookData.price > 0 && !userOwnsBook)}
              class:cursor-not-allowed={!bookData.has_pdf || loadingPdf || (bookData.price > 0 && !userOwnsBook)}
              on:click={handlePreview}
              disabled={!bookData.has_pdf || loadingPdf || (bookData.price > 0 && !userOwnsBook)}
            >
              {#if loadingPdf}
                <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-orange-400"></div>
              {:else}
                <svg class="w-5 h-4" fill="currentColor" viewBox="0 0 16 12">
                  <path d="M8 0C4.5 0 1.6 2.4 0 6c1.6 3.6 4.5 6 8 6s6.4-2.4 8-6c-1.6-3.6-4.5-6-8-6zm0 10c-2.2 0-4-1.8-4-4s1.8-4 4-4 4 1.8 4 4-1.8 4-4 4z"/>
                  <circle cx="8" cy="6" r="2"/>
                </svg>
              {/if}
              <span class="text-lg font-bold text-zinc-950">
                {loadingPdf ? 'กำลังโหลด...' : 
                 (bookData.price > 0 && !userOwnsBook) ? 'ต้องซื้อก่อน' : 'ดูตัวอย่าง'}
              </span>
            </button>
            
            <button 
              class="flex-1 bg-white rounded-xl shadow-lg px-6 py-4 flex items-center justify-center gap-3 hover:shadow-xl transition-shadow"
              on:click={handleReview}
            >
              <svg class="w-6 h-5" fill="currentColor" viewBox="0 0 20 16">
                <path d="M18 0H2C0.9 0 0 0.9 0 2v12c0 1.1 0.9 2 2 2h16c1.1 0 2-0.9 2-2V2c0-1.1-0.9-2-2-2zM6 4h8v2H6V4zm8 6H6V8h8v2zm2-8v12H4V2h12z"/>
              </svg>
              <span class="text-lg font-bold text-zinc-950">รีวิว ({reviewCount})</span>
            </button>
          </div>
          
          <button 
            class="w-full rounded-2xl shadow-xl px-8 py-5 flex items-center justify-center gap-4 transition-colors relative"
            class:bg-zinc-950={displayPrice > 0 && !userOwnsBook}
            class:bg-green-600={displayPrice === 0 || userOwnsBook}
            class:hover:bg-zinc-800={displayPrice > 0 && !userOwnsBook}
            class:hover:bg-green-700={displayPrice === 0 || userOwnsBook}
            class:opacity-50={purchasingBook}
            class:cursor-not-allowed={purchasingBook}
            on:click={handlePurchase}
            disabled={purchasingBook}
          >
            {#if purchasingBook}
              <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
              <span class="text-white text-xl font-bold">กำลังซื้อ...</span>
            {:else}
              <span class="text-white text-xl font-bold">
                {userOwnsBook ? 'เปิดอ่าน' : 
                 displayPrice === 0 ? 'อ่านฟรี' : 
                 userPoints < displayPrice ? `ต้องการ ${displayPrice - userPoints} Points` : 'ซื้อเล่มนี้'}
              </span>
              <div class="rounded-full px-3 py-2 flex items-center gap-1"
                   class:bg-orange-400={displayPrice > 0 && !userOwnsBook}
                   class:bg-green-500={displayPrice === 0 || userOwnsBook}>
                <img src={SANPoint} alt="SAN Logo" class="w-4 h-4 object-contain" />
                <span class="text-white text-sm font-bold">
                  {userOwnsBook ? 'เป็นเจ้าของแล้ว' : priceText}
                </span>
              </div>
            {/if}
          </button>
        </div>
      </div>
    </div>
  {/if}

  <!-- Simple Responsive PDF Modal -->
  {#if showPdfModal}
    <div 
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-75 animate-fade-in"
      on:click|self={closePdfModal}
    >
      <div class="relative w-full h-full max-w-7xl max-h-full m-2 sm:m-4 bg-white rounded-none sm:rounded-lg shadow-2xl animate-scale-in overflow-hidden">
        <!-- Modal Header -->
        <div class="flex items-center justify-between p-3 sm:p-4 bg-gray-50 border-b border-gray-200">
          <div class="flex items-center space-x-2 sm:space-x-3 flex-1 min-w-0">
            <Book class="w-5 h-5 sm:w-6 sm:h-6 text-gray-600 flex-shrink-0" />
            <h3 class="text-sm sm:text-lg font-semibold text-gray-900 truncate">{bookData.title}</h3>
          </div>
          <div class="flex items-center space-x-1 sm:space-x-2 flex-shrink-0">
            <button
              class="p-1.5 sm:p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full transition-colors"
              on:click={downloadPdf}
              title="ดาวน์โหลด PDF"
            >
              <Download class="w-4 h-4 sm:w-5 sm:h-5" />
            </button>
            <button
              class="p-1.5 sm:p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full transition-colors"
              on:click={closePdfModal}
              title="ปิด"
            >
              <X class="w-5 h-5 sm:w-6 sm:h-6" />
            </button>
          </div>
        </div>
        
        <!-- PDF Viewer - Fully Responsive -->
        <div class="w-full h-full overflow-auto bg-gray-100" style="height: calc(100% - 60px);">
          {#if pdfUrl}
            <div class="w-full h-full flex items-center justify-center p-2 sm:p-4">
              <div class="w-full max-w-full h-full bg-white shadow-lg rounded-none sm:rounded-lg overflow-hidden">
                <iframe
                  src={pdfUrl}
                  class="w-full h-full border-0"
                  style="min-height: 70vh;"
                  title="PDF Viewer - {bookData.title}"
                  loading="lazy"
                ></iframe>
              </div>
            </div>
          {:else}
            <div class="flex items-center justify-center h-full">
              <div class="text-center p-4">
                <div class="animate-spin rounded-full h-8 w-8 sm:h-12 sm:w-12 border-b-2 border-orange-400 mx-auto mb-4"></div>
                <p class="text-gray-600 text-sm sm:text-base">กำลังโหลด PDF...</p>
              </div>
            </div>
          {/if}
        </div>
      </div>
    </div>
  {/if}
  {#if showReviewModal}
  <ReviewModal 
    bookId={bookData.id}
    bookTitle={bookData.title}
    userOwnsBook={userOwnsBook}
    bookIsFree={displayPrice === 0}
    on:close={() => showReviewModal = false}
  />
{/if}
</div>

<style>
  @keyframes fade-in {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  @keyframes scale-in {
    from { 
      opacity: 0;
      transform: scale(0.95) translateY(-10px);
    }
    to { 
      opacity: 1;
      transform: scale(1) translateY(0);
    }
  }

  .animate-fade-in {
    animation: fade-in 0.2s ease-out;
  }

  .animate-scale-in {
    animation: scale-in 0.3s ease-out;
  }

  /* Mobile optimizations */
  @media (max-width: 640px) {
    iframe {
      height: calc(100vh - 120px) !important;
      min-height: calc(100vh - 120px) !important;
    }
  }

  /* Tablet and desktop */
  @media (min-width: 641px) {
    iframe {
      height: calc(100vh - 140px) !important;
      min-height: 600px !important;
    }
  }

  /* Ensure the PDF modal takes full screen on mobile */
  @media (max-width: 640px) {
    .fixed.inset-0 > div {
      margin: 0 !important;
      border-radius: 0 !important;
      width: 100% !important;
      height: 100% !important;
      max-width: 100% !important;
      max-height: 100% !important;
    }
  }
</style>
