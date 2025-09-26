<script>
  import { onMount, createEventDispatcher } from 'svelte';
  
  const dispatch = createEventDispatcher();
  
  let isBookmarked = false;
  let bookData = {
    title: "Yves Saint Laurent",
    author: "Author",
    rating: 4.5,
    description: "A spectacular visual journey through 40 years of haute couture from one of the best-known and most trend-setting brands in fashion.",
    cover: ""
  };
  
  onMount(() => {
    // Get book data from sessionStorage
    const selectedBook = sessionStorage.getItem('selectedBook');
    if (selectedBook) {
      bookData = JSON.parse(selectedBook);
    }
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
    console.log('Purchase clicked');
  }
</script>

<div class="min-h-screen bg-white">
  <!-- Mobile Layout -->
  <div class="lg:hidden w-full max-w-sm mx-auto relative overflow-hidden">
    <!-- Header -->
    <div class="flex justify-between items-center p-6">
      <button class="w-6 h-6 flex items-center justify-center" on:click={goBack}>
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
        </svg>
      </button>
      
      <div class="flex gap-3">
        <button 
          class="w-6 h-6 flex items-center justify-center"
          on:click={toggleBookmark}
          class:text-red-500={isBookmarked}
        >
          <svg class="w-5 h-5" fill={isBookmarked ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
          </svg>
        </button>
        
        <button class="w-6 h-6 flex items-center justify-center">
          <svg class="w-1 h-4" fill="currentColor" viewBox="0 0 4 16">
            <circle cx="2" cy="2" r="2"/>
            <circle cx="2" cy="8" r="2"/>
            <circle cx="2" cy="14" r="2"/>
          </svg>
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
      
      <div class="flex items-center justify-center gap-1 mb-6">
        <div class="flex text-yellow-400">
          {#each Array(5) as _, i}
            <span class={i < Math.floor(bookData.rating) ? "text-yellow-400" : "text-gray-300"}>⭐</span>
          {/each}
        </div>
        <span class="text-sm font-medium text-zinc-950 ml-2">{bookData.rating}</span>
        <span class="text-sm text-zinc-500">/ 5.0</span>
      </div>
      
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
        class="w-full bg-zinc-950 rounded-[20px] shadow-lg px-28 py-4 flex items-center justify-center gap-2.5 hover:bg-zinc-800 transition-colors"
        on:click={handlePurchase}
      >
        <span class="text-white text-base font-bold">ซื้อเลยตอนนี้</span>
        <div class="bg-orange-400 rounded-full px-2 py-1 flex items-center gap-1">
          <svg class="w-2.5 h-1.5 text-white" fill="currentColor" viewBox="0 0 10 6">
            <path d="M0 0h4v2H0V0zM6 0h4v2H6V0zM0 2h10v2H0V2zM0 4h4v2H0V4zM6 4h4v2H6V4z"/>
          </svg>
          <span class="text-white text-xs font-bold">102</span>
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
              <h1 class="text-3xl font-bold text-center mb-4">YVES SAINT LAURENT</h1>
              <p class="text-lg font-light italic text-center mb-12">haute couture</p>
              <p class="text-2xl font-semibold text-center">CATWALK</p>
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
          <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
        </button>
        
        <div class="flex gap-4">
          <button 
            class="w-8 h-8 flex items-center justify-center text-gray-600 hover:text-gray-900"
            on:click={toggleBookmark}
            class:text-red-500={isBookmarked}
          >
            <svg class="w-6 h-6" fill={isBookmarked ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
            </svg>
          </button>
          
          <button class="w-8 h-8 flex items-center justify-center text-gray-600 hover:text-gray-900">
            <svg class="w-2 h-6" fill="currentColor" viewBox="0 0 4 16">
              <circle cx="2" cy="2" r="2"/>
              <circle cx="2" cy="8" r="2"/>
              <circle cx="2" cy="14" r="2"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Book Info -->
      <div class="mb-12">
        <h1 class="text-5xl font-bold text-zinc-950 mb-4">{bookData.title}</h1>
        <p class="text-lg text-zinc-500 mb-6">แต่งโดย {bookData.author}</p>
        
        <div class="flex items-center gap-2 mb-8">
          <div class="flex text-yellow-400 text-xl">
            {#each Array(5) as _, i}
              <span class={i < Math.floor(bookData.rating) ? "text-yellow-400" : "text-gray-300"}>⭐</span>
            {/each}
          </div>
          <span class="text-xl font-medium text-zinc-950 ml-2">{bookData.rating}</span>
          <span class="text-xl text-zinc-500">/ 5.0</span>
        </div>
        
        <p class="text-lg text-zinc-600 leading-relaxed mb-12 max-w-lg">
          {bookData.description}
        </p>
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
          class="w-full bg-zinc-950 rounded-2xl shadow-xl px-8 py-5 flex items-center justify-center gap-4 hover:bg-zinc-800 transition-colors"
          on:click={handlePurchase}
        >
          <span class="text-white text-xl font-bold">ซื้อเลยตอนนี้</span>
          <div class="bg-orange-400 rounded-full px-3 py-2 flex items-center gap-2">
            <svg class="w-3 h-2 text-white" fill="currentColor" viewBox="0 0 10 6">
              <path d="M0 0h4v2H0V0zM6 0h4v2H6V0zM0 2h10v2H0V2zM0 4h4v2H0V4zM6 4h4v2H6V4z"/>
            </svg>
            <span class="text-white text-sm font-bold">102</span>
          </div>
        </button>
      </div>
    </div>
  </div>
</div>