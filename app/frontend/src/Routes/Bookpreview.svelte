<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import SANPoint from "../assets/SAN_Point_White.svg";
  import { Book, Bookmark, CircleArrowLeft } from '@lucide/svelte';
  
  const dispatch = createEventDispatcher();
  
  let isBookmarked = false;
  let showDescription = false;
  let bookData = {
    title: "The Book is unavailable",
    author: "unknown",
    rating: 5,
    price: 0, // Default price
    description: "Internal error: Book data not found.",
    cover: ""
  };
  
  onMount(() => {
    // Get book data from sessionStorage
    const selectedBook = sessionStorage.getItem('selectedBook');
    if (selectedBook) {
      const parsedBook = JSON.parse(selectedBook);
      bookData = {
        ...bookData,
        ...parsedBook,
        price: parsedBook.price ?? 0 // Ensure price is not undefined/null
      };
    }
    console.log('Book data loaded:', bookData); // Debug log
  });
  
  function goBack() {
    dispatch('navigate', 'home');
  }
  
  function toggleBookmark() {
    isBookmarked = !isBookmarked;
  }
  
  function handlePreview() {
    console.log('Preview clicked');
  }
  
  function handleReview() {
    console.log('Review clicked');
  }
  
  function handlePurchase() {
    console.log('Purchase clicked for price:', bookData.price);
    if (bookData.price === 0) {
      console.log('Free book - no payment required');
    } else {
      console.log(`Payment required: ${bookData.price} points`);
    }
  }

  // Helper function to format price display
  function formatPrice(price) {
    if (price === undefined || price === null || price === 0) {
      return 'ฟรี';
    }
    return price.toString();
  }

  // Reactive statement to ensure price is always a number
  $: displayPrice = bookData.price ?? 0;
  $: priceText = displayPrice === 0 ? 'ฟรี' : displayPrice.toString();
</script>

<div class="min-h-screen bg-white">
  <!-- Mobile Layout -->
  <div class="lg:hidden w-full mx-auto relative overflow-hidden">
    <!-- Header -->
    <div class="flex justify-between items-center p-6">
      <button class="w-6 h-6 flex items-center justify-center" on:click={goBack}>
        <CircleArrowLeft class="w-6 h-6 text-gray-600" />
      </button>
      
      <div class="flex gap-3">
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
          {#if bookData.cover && !bookData.cover.includes('placehold')}
            <img src={bookData.cover} alt={bookData.title} class="w-full h-full object-cover" />
          {:else}
            <div class="absolute inset-0 flex flex-col items-center justify-center text-black px-8">
              <h1 class="text-xl font-bold text-center mb-2">IMAGE BOOK COVER</h1>
              <p class="text-sm font-light italic text-center mb-8">CAN NOT BE LOAD</p>
            </div>
          {/if}
        </div>
        <div class="w-[1px] h-80 absolute left-2.5 top-0 bg-stone-700 z-10"></div>
      </div>
    </div>

    <!-- Book Info -->
    <div class="px-6 text-center mb-8">
      <h2 class="text-2xl font-semibold text-zinc-950 mb-2">{bookData.title}</h2>
      <p class="text-xs text-zinc-500 mb-4">แต่งโดย {bookData.author}</p>
      
      <div class="flex items-center justify-center gap-1 mb-4">
        <div class="flex text-yellow-400">
          {#each Array(5) as _, i}
            <span class={i < Math.floor(bookData.rating) ? "text-yellow-400" : "text-gray-300"}>⭐</span>
          {/each}
        </div>
        <span class="text-sm font-medium text-zinc-950 ml-2">{bookData.rating}</span>
        <span class="text-sm text-zinc-500">/ 5.0</span>
      </div>

      <!-- Price Display -->
      <!-- <div class="flex items-center justify-center mb-6">
        <div class="flex items-center gap-2 bg-gray-100 rounded-full px-4 py-2">
          <img src={SANPoint} alt="SAN Logo" class="w-4 h-4 object-contain" />
          <span class="text-sm font-bold text-zinc-800">
            {#if displayPrice === 0}
              ฟรี
            {:else}
              {displayPrice} Points
            {/if}
          </span>
        </div>
      </div> -->
      
      <p class="text-sm text-zinc-500 opacity-50 leading-normal mb-8">
        {bookData.description}
      </p>
    </div>

    <!-- Action Buttons -->
    <div class="px-6 mb-8">
      <div class="flex gap-4 mb-4">
        <button 
          class="flex-1 bg-white rounded-lg shadow-md px-4 py-3 flex items-center justify-center gap-2 hover:shadow-lg transition-shadow"
          on:click={handlePreview}
        >
          <svg class="w-4 h-3" fill="currentColor" viewBox="0 0 16 12">
            <path d="M8 0C4.5 0 1.6 2.4 0 6c1.6 3.6 4.5 6 8 6s6.4-2.4 8-6c-1.6-3.6-4.5-6-8-6zm0 10c-2.2 0-4-1.8-4-4s1.8-4 4-4 4 1.8 4 4-1.8 4-4 4z"/>
            <circle cx="8" cy="6" r="2"/>
          </svg>
          <span class="text-sm font-bold text-zinc-950">ดูตัวอย่าง</span>
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
        class="w-full rounded-[20px] shadow-lg px-28 py-4 flex items-center justify-center gap-2.5 transition-colors"
        class:bg-zinc-950={displayPrice > 0}
        class:bg-green-600={displayPrice === 0}
        class:hover:bg-zinc-800={displayPrice > 0}
        class:hover:bg-green-700={displayPrice === 0}
        on:click={handlePurchase}
      >
        <span class="text-white text-base font-bold">
          {displayPrice === 0 ? 'อ่านฟรี' : 'ซื้อเลยตอนนี้'}
        </span>
        <div class="rounded-full px-2 py-1 flex items-center gap-1"
             class:bg-orange-400={displayPrice > 0}
             class:bg-green-500={displayPrice === 0}>
          <img src={SANPoint} alt="SAN Logo" class="w-4 h-4 object-contain" />
          <span class="text-white text-xs font-bold">{priceText}</span>
        </div>
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
          {#if bookData.cover && !bookData.cover.includes('placehold')}
            <img src={bookData.cover} alt={bookData.title} class="w-full h-full object-cover" />
          {:else}
            <div class="absolute inset-0 flex flex-col items-center justify-center text-black px-12">
              <h1 class="text-3xl font-bold text-center mb-4">{bookData.title.toUpperCase()}</h1>
              <p class="text-lg font-light italic text-center mb-12">แต่งโดย {bookData.author}</p>
              <p class="text-2xl font-semibold text-center">หนังสือ</p>
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
  <p class="text-lg text-zinc-500 mb-6">แต่งโดย {bookData.author}</p>
  
  <div class="flex items-center gap-2 mb-6">
    <div class="flex text-yellow-400 text-xl">
      {#each Array(5) as _, i}
        <span class={i < Math.floor(bookData.rating) ? "text-yellow-400" : "text-gray-300"}>⭐</span>
      {/each}
    </div>
    <span class="text-xl font-medium text-zinc-950 ml-2">{bookData.rating}</span>
    <span class="text-xl text-zinc-500">/ 5.0</span>
  </div>

  <!-- Price Display Desktop -->
  <!-- <div class="flex items-center mb-8">
    <div class="flex items-center gap-3 bg-gray-100 rounded-full px-6 py-3">
      <img src={SANPoint} alt="SAN Logo" class="w-5 h-5 object-contain" />
      <span class="text-lg font-bold text-zinc-800">
        {#if displayPrice === 0}
          ฟรี
        {:else}
          {displayPrice} Points
        {/if}
      </span>
    </div>
  </div> -->

  <!-- กล่องรายละเอียดหนังสือแบบเปิด-ปิดได้ -->
  <div class="border border-zinc-300 rounded-lg p-6 bg-white shadow-sm mb-12 w-full">
    <div class="flex justify-between items-center cursor-pointer" on:click={() => showDescription = !showDescription}>
      <h3 class="text-lg font-medium text-zinc-800">ลายละเอียดหนังสือ</h3>
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
            class="flex-1 bg-white rounded-xl shadow-lg px-6 py-4 flex items-center justify-center gap-3 hover:shadow-xl transition-shadow"
            on:click={handlePreview}
          >
            <svg class="w-5 h-4" fill="currentColor" viewBox="0 0 16 12">
              <path d="M8 0C4.5 0 1.6 2.4 0 6c1.6 3.6 4.5 6 8 6s6.4-2.4 8-6c-1.6-3.6-4.5-6-8-6zm0 10c-2.2 0-4-1.8-4-4s1.8-4 4-4 4 1.8 4 4-1.8 4-4 4z"/>
              <circle cx="8" cy="6" r="2"/>
            </svg>
            <span class="text-lg font-bold text-zinc-950">ดูตัวอย่าง</span>
          </button>
          
          <button 
            class="flex-1 bg-white rounded-xl shadow-lg px-6 py-4 flex items-center justify-center gap-3 hover:shadow-xl transition-shadow"
            on:click={handleReview}
          >
            <svg class="w-6 h-5" fill="currentColor" viewBox="0 0 20 16">
              <path d="M18 0H2C0.9 0 0 0.9 0 2v12c0 1.1 0.9 2 2 2h16c1.1 0 2-0.9 2-2V2c0-1.1-0.9-2-2-2zM6 4h8v2H6V4zm8 6H6V8h8v2zm2-8v12H4V2h12z"/>
            </svg>
            <span class="text-lg font-bold text-zinc-950">รีวิว</span>
          </button>
        </div>
        
        <button 
          class="w-full rounded-2xl shadow-xl px-8 py-5 flex items-center justify-center gap-4 transition-colors"
          class:bg-zinc-950={displayPrice > 0}
          class:bg-green-600={displayPrice === 0}
          class:hover:bg-zinc-800={displayPrice > 0}
          class:hover:bg-green-700={displayPrice === 0}
          on:click={handlePurchase}
        >
          <span class="text-white text-xl font-bold">
            {displayPrice === 0 ? 'อ่านฟรี' : 'ซื้อเลยตอนนี้'}
          </span>
          <div class="rounded-full px-3 py-2 flex items-center gap-1"
               class:bg-orange-400={displayPrice > 0}
               class:bg-green-500={displayPrice === 0}>
            <img src={SANPoint} alt="SAN Logo" class="w-4 h-4 object-contain" />
            <span class="text-white text-sm font-bold">{priceText}</span>
          </div>
        </button>
      </div>
    </div>
  </div>
</div>