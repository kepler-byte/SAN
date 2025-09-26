<script>
  import { clearAuth } from "../lib/auth";
  import { House } from "@lucide/svelte";
  import { createEventDispatcher } from 'svelte';
  
  const dispatch = createEventDispatcher();
  
  function logout() {
    clearAuth();
    location.reload();
  }
  
  let username = "Username";
  let points = 999;

  let categories = ["ทั้งหมด", "ความรู้", "นิยาย", "มังงะ", "ยอดนิยม"];
  let selected = "ทั้งหมด";

  let popularBooks = [
    { title: "Fashionopolis", author: "Dana Thomas", cover: "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400&h=600&fit=crop", rating: 4.2, description: "A fascinating journey through the world of fashion and its impact on society." },
    { title: "Chanel", author: "Paul Morand", cover: "https://images.unsplash.com/photo-1590736969955-71cc94901144?w=400&h=600&fit=crop", rating: 4.5, description: "The story of the iconic fashion house and its revolutionary designs." },
    { title: "Calligraphy", author: "Julian Waters", cover: "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&h=600&fit=crop", rating: 4.0, description: "Master the art of beautiful handwriting with this comprehensive guide." },
    { title: "Typography", author: "Ellen Lupton", cover: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=600&fit=crop", rating: 4.3, description: "Explore the world of fonts and their psychological impact on design." },
    { title: "Modern Art", author: "Amy Dempsey", cover: "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=600&fit=crop", rating: 4.1, description: "A comprehensive overview of contemporary art movements and their significance." },
    { title: "Design Rules", author: "Stefan Sagmeister", cover: "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=400&h=600&fit=crop", rating: 4.4, description: "Essential principles every designer should know for creating impactful work." },
    { title: "Color Theory", author: "Josef Albers", cover: "https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=400&h=600&fit=crop", rating: 4.6, description: "Understanding the psychology and application of colors in design and art." },
    { title: "Webtoon Guide", author: "Kim Jung-gi", cover: "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=600&fit=crop", rating: 4.2, description: "Complete guide to creating and publishing successful webtoons." },
    { title: "Manga World", author: "Takeshi Obata", cover: "https://images.unsplash.com/photo-1544716278-e513176f20a5?w=400&h=600&fit=crop", rating: 4.3, description: "Dive into the fascinating world of Japanese manga and its cultural impact." },
    { title: "Illustration", author: "Andrea Joseph", cover: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=600&fit=crop", rating: 4.0, description: "Learn professional illustration techniques from concept to final artwork." }
  ];

  let newBooks = [
    {
      title: "Yves Saint Laurent",
      author: "Suzy Menkes",
      cover: "https://images.unsplash.com/photo-1594736797933-d0c6a0d48e5e?w=400&h=600&fit=crop",
      rating: 4.5,
      description: "A spectacular visual journey through 40 years of haute couture from one of the best-known and most trend-setting brands in fashion."
    },
    {
      title: "The Book of Signs",
      author: "Rudolf Koch",
      cover: "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&h=600&fit=crop",
      rating: 4.2,
      description: "A comprehensive guide to understanding symbols and their meanings throughout history and culture."
    }
  ];

  // Function to handle book click and navigate to preview
  function handleBookClick(book) {
    // Store the selected book data in sessionStorage for the preview page
    sessionStorage.setItem('selectedBook', JSON.stringify(book));
    
    // Navigate to book preview page
    dispatch('navigate', 'bookpreview');
  }
</script>
<!-- Header -->
<div class="p-6 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
  <div class="flex items-center gap-3">
    <div class="w-8 h-8 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
      <House class="w-4 h-4 text-gray-600 dark:text-gray-300" />
    </div>
    <h1 class="text-lg font-semibold text-gray-900 dark:text-gray-100">หน้าหลัก</h1>
  </div>
</div>

<!-- Main Content -->
<div class="min-h-screen bg-white dark:bg-gray-900 px-6 py-5 space-y-6">
  <!-- Header -->
  <div class="flex items-center justify-between">
    <div class="flex items-center gap-3 md:gap-4">
      <img src="https://placehold.co/40x40" class="w-10 h-10 md:w-14 md:h-14 lg:w-16 lg:h-16 rounded-lg shadow" alt="Profile" />
      <div>
        <p class="text-sm md:text-base lg:text-lg text-gray-700 dark:text-gray-300">สวัสดีตอนเช้า</p>
        <p class="text-sm md:text-lg lg:text-xl font-bold text-gray-900 dark:text-gray-100">{username}</p>
      </div>
    </div>
    <div class="bg-orange-400 text-white px-3 py-1.5 md:px-4 md:py-2 lg:px-5 lg:py-3 rounded-lg font-bold text-xs md:text-sm lg:text-base flex items-center gap-1 md:gap-2">
      <span class="md:text-lg lg:text-xl">{points}</span>
      <span class="text-[10px] md:text-xs lg:text-sm">฿</span>
    </div>
  </div>

  <!-- Search -->
  <div class="flex items-center justify-between bg-white dark:bg-gray-800 px-3 py-2 rounded-lg shadow">
    <input
      type="text"
      placeholder="ค้นหาหนังสือของคุณ"
      class="flex-1 text-sm text-gray-500 dark:text-gray-400 focus:outline-none bg-transparent"
    />
    <button class="p-2 bg-orange-400 rounded-md">
      <div class="w-3 h-3 bg-white"></div>
    </button>
  </div>

  <!-- Categories -->
  <div class="flex gap-2 overflow-x-auto">
    {#each categories as cat}
      <button
        class="px-3 py-1 rounded-md text-xs whitespace-nowrap
               {cat === selected 
                 ? 'bg-orange-400 text-white' 
                 : 'bg-neutral-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200'}"
        on:click={() => (selected = cat)}
      >
        {cat}
      </button>
    {/each}
  </div>

  <!-- Popular Books -->
  <div>
    <h2 class="text-xl font-bold mb-3 text-gray-900 dark:text-gray-100">หนังสือยอดนิยม</h2>
    <div class="flex gap-6 overflow-x-auto overflow-y-hidden scrollbar-hide pb-2">
      {#each popularBooks as book}
        <div 
          class="flex-none w-28 sm:w-36 md:w-44 lg:w-56 cursor-pointer transform hover:scale-105 transition-transform duration-200"
          on:click={() => handleBookClick(book)}
          on:keydown={(e) => e.key === 'Enter' && handleBookClick(book)}
          tabindex="0"
          role="button"
        >
          <img
            src={book.cover}
            alt={book.title}
            class="w-full h-40 sm:h-52 md:h-64 lg:h-80 object-cover rounded-md shadow hover:shadow-lg transition-shadow duration-200"
          />
          <p class="mt-2 font-semibold text-sm md:text-base lg:text-lg text-gray-900 dark:text-gray-100 truncate">{book.title}</p>
          <p class="text-xs md:text-sm text-gray-500 dark:text-gray-400 truncate">แต่งโดย {book.author}</p>
          {#if book.rating}
            <div class="flex items-center mt-1">
              <div class="flex text-yellow-400 text-xs">
                {#each Array(5) as _, i}
                  <span class={i < Math.floor(book.rating) ? "text-yellow-400" : "text-gray-400 dark:text-gray-500"}>★</span>
                {/each}
              </div>
              <span class="text-xs text-gray-500 dark:text-gray-400 ml-1">{book.rating}</span>
            </div>
          {/if}
        </div>
      {/each}
    </div>
  </div>

  <!-- New Books -->
  <div>
    <h2 class="text-xl font-bold mb-3 text-gray-900 dark:text-gray-100">หนังสือใหม่</h2>
    <div class="space-y-4">
      {#each newBooks as book}
        <div 
          class="flex items-center gap-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 p-2 rounded-lg transition-colors duration-200"
          on:click={() => handleBookClick(book)}
          on:keydown={(e) => e.key === 'Enter' && handleBookClick(book)}
          tabindex="0"
          role="button"
        >
          <img 
            src={book.cover} 
            alt={book.title} 
            class="w-16 h-24 rounded-md shadow hover:shadow-lg transition-shadow duration-200" 
          />
          <div class="flex-1">
            <p class="font-semibold text-sm text-gray-900 dark:text-gray-100">{book.title}</p>
            <p class="text-xs text-gray-500 dark:text-gray-400">แต่งโดย {book.author}</p>
            {#if book.rating > 0}
              <div class="flex items-center mt-1">
                <div class="flex">
                  {#each Array(5) as _, i}
                    <span class={i < Math.floor(book.rating) ? "text-yellow-400" : "text-gray-400 dark:text-gray-500"}>★</span>
                  {/each}
                </div>
                <span class="text-xs text-gray-500 dark:text-gray-400 ml-1">{book.rating}</span>
              </div>
            {/if}
          </div>
          <button class="p-2">
            <svg class="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 5v14l7-7 7 7V5H5z"/>
            </svg>
          </button>
        </div>
      {/each}
    </div>
  </div>
</div>