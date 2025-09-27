<script>
  import { House, Search, CircleAlert, Bookmark, Filter } from "@lucide/svelte";
  import { createEventDispatcher, onMount } from "svelte";
  import { getAllBooks, getCurrentUser, getBooksByCategory } from "../lib/api.js";
  import SANPoint from "../assets/SAN_Point_White.svg";

  const dispatch = createEventDispatcher();

  // Configurable API base (use Vite env var)
  const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

  // User state
  let username = "User";
  let points = 0;

  // Loading & error
  let loading = true;
  let error = null;

  // Search & categories
  let searchQuery = "";
  let mainCategories = ["ยอดนิยม", "มาใหม่", "ทั้งหมด"];
  let filterCategories = ["ความรู้", "นิยาย", "มังงะ", "ศิลปะ", "วิทยาศาสตร์", "ประวัติศาสตร์", "ธุรกิจ", "การศึกษา", "เทคโนโลยี", "สุขภาพ", "การเงิน", "จิตวิทยา", "อื่นๆ"];
  let selected = "ยอดนิยม";
  let selectedFilter = null; // For category filter
  let showFilterDropdown = false;

  // Raw book data
  let allBooks = [];
  let categoryBooks = []; // Books filtered by category

  // Category loading state
  let categoryLoading = false;

  // Reactive derived data
  $: filteredBooks = (() => {
    let books = selected === "ทั้งหมด" ? allBooks : categoryBooks;
    
    // Apply category filter if selected
    if (selectedFilter) {
      books = books.filter(book => book.category === selectedFilter);
    }
    
    // Apply search query
    if (searchQuery.trim()) {
      books = books.filter((book) => {
        const titleMatch = book.title?.toLowerCase().includes(searchQuery.toLowerCase());
        const authorMatch = (book.author || "").toLowerCase().includes(searchQuery.toLowerCase());
        return titleMatch || authorMatch;
      });
    }
    
    return books;
  })();

  // Get books for display based on selected category and search
  $: booksToDisplay = selected === "ยอดนิยม" 
    ? filteredBooks.sort((a, b) => (b.rating || 0) - (a.rating || 0))
    : selected === "มาใหม่"
    ? filteredBooks.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    : filteredBooks;

  $: displayedPopular = booksToDisplay
    .slice(0, 10)
    .map((book) => ({
      ...book,
      price: book.price ?? 0,
      cover: book.cover
        ? `${API_BASE}${book.cover}`
        : `https://images.unsplash.com/photo-${Math.random().toString(36).substr(2, 9)}?w=400&h=600&fit=crop`,
    }));

  $: displayedNew = booksToDisplay
    .slice(0, 5)
    .map((book) => ({
      ...book,
      price: book.price ?? 0,
      cover: book.cover
        ? `${API_BASE}${book.cover}`
        : `https://images.unsplash.com/photo-${Math.random().toString(36).substr(2, 9)}?w=400&h=600&fit=crop`,
    }));

  // Fetch data on mount
  onMount(async () => {
    try {
      loading = true;
      error = null;

      // Load user
      const userData = await getCurrentUser();
      username = userData.username || userData.name || "User";
      points = userData.points || 0;

      // Load all books initially
      const booksResponse = await getAllBooks(0, 50);
      allBooks = Array.isArray(booksResponse) ? booksResponse : [];
      categoryBooks = allBooks; // Initialize with all books

      console.log(
        "Loaded books:",
        allBooks.map((b) => ({ title: b.title, price: b.price }))
      );
    } catch (err) {
      console.error("Failed to load data:", err);
      error = err.message || "ไม่สามารถโหลดข้อมูลได้";
      allBooks = [];
      categoryBooks = [];
    } finally {
      loading = false;
    }
  });

  // Handle category change with API filtering
  async function handleCategoryChange(category) {
    if (selected === category) return; // Don't reload if same category
    
    selected = category;
    selectedFilter = null; // Reset filter when changing main category
    
    // If "ทั้งหมด" is selected, use all books
    if (category === "ทั้งหมด") {
      categoryBooks = allBooks;
      return;
    }
    
    // For special categories, filter from all books
    if (category === "ยอดนิยม" || category === "มาใหม่") {
      categoryBooks = allBooks;
      return;
    }
    
    // For other cases, use all books as base
    categoryBooks = allBooks;
  }

  // Handle filter selection
  function handleFilterChange(filter) {
    selectedFilter = selectedFilter === filter ? null : filter; // Toggle filter
    showFilterDropdown = false;
  }

  // Clear all filters
  function clearFilters() {
    selectedFilter = null;
    searchQuery = "";
    showFilterDropdown = false;
  }

  // Handle book selection
  function handleBookClick(book) {
    try {
      const bookWithPrice = {
        ...book,
        price: book.price ?? 0,
      };
      console.log("Selecting book:", bookWithPrice);
      sessionStorage.setItem("selectedBook", JSON.stringify(bookWithPrice));
      dispatch("navigate", "bookpreview");
    } catch (e) {
      console.error("Failed to save book to session:", e);
    }
  }

  // Helper function to format price
  function formatPrice(price) {
    return price === undefined || price === null || price === 0
      ? "ฟรี"
      : `${price}`;
  }

  // Get section title based on selected category
  function getSectionTitle() {
    let title = "";
    switch(selected) {
      case "ยอดนิยม": title = "หนังสือยอดนิยม"; break;
      case "มาใหม่": title = "หนังสือใหม่"; break;
      case "ทั้งหมด": title = "หนังสือทั้งหมด"; break;
      default: title = selected;
    }
    
    // Add filter info if applied
    if (selectedFilter) {
      title += ` - ${selectedFilter}`;
    }
    
    return title;
  }
</script>

<div
  class="p-6 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800"
>
  <div class="flex items-center gap-3">
    <div
      class="w-8 h-8 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center"
    >
      <House class="w-4 h-4 text-gray-600 dark:text-gray-300" />
    </div>
    <h1 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
      หน้าหลัก
    </h1>
  </div>
</div>

<div class="min-h-screen bg-white px-6 py-5 space-y-6">
  {#if loading}
    <div class="flex justify-center items-center h-64">
      <div
        class="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-400"
      ></div>
      <span class="ml-2 text-gray-600">กำลังโหลดข้อมูล...</span>
    </div>
  {:else if error}
    <div class="bg-red-50 border border-red-200 rounded-lg p-4">
      <div class="flex">
        <CircleAlert class="w-6 h-6 text-red-600" />
        <p class="ml-3 text-sm text-red-800">เกิดข้อผิดพลาด: {error}</p>
      </div>
    </div>
  {:else}
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3 md:gap-4">
        <img
          src="https://placehold.co/40x40"
          class="w-10 h-10 md:w-14 md:h-14 lg:w-16 lg:h-16 rounded-lg shadow"
          alt="Profile"
        />
        <div>
          <p class="text-sm md:text-base lg:text-lg text-gray-700">
            สวัสดีตอนเช้า
          </p>
          <p class="text-sm md:text-lg lg:text-xl font-bold">{username}</p>
        </div>
      </div>
      <div
        class="bg-orange-400 text-white px-3 py-1.5 md:px-4 md:py-2 lg:px-5 lg:py-3 rounded-[9999px] font-bold text-xs md:text-sm lg:text-base flex items-center gap-1"
      >
        <span class="md:text-lg lg:text-xl">{points}</span>
        <img src={SANPoint} alt="SAN Logo" class="w-4 h-4 object-contain" />
      </div>
    </div>

    <!-- Search + Filter -->
<div class="relative">
  <div
    class="flex items-center justify-between bg-white px-3 py-2 rounded-lg shadow"
  >
    <input
      type="text"
      placeholder="ค้นหาหนังสือของคุณ"
      class="flex-1 text-sm text-gray-500 focus:outline-none"
      bind:value={searchQuery}
      aria-label="ค้นหาหนังสือ"
    />
    <button
      class="p-2 bg-orange-400 rounded-md"
      on:click={() => showFilterDropdown = !showFilterDropdown}
      aria-label="ตัวกรองหนังสือ"
    >
      <Filter class="w-4 h-4 text-white" />
    </button>
  </div>

  <!-- Dropdown Filter -->
  {#if showFilterDropdown}
    <div
      class="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-10"
    >
      <div class="p-2">
        {#each filterCategories as filter}
          <button
            class="w-full text-left px-3 py-2 text-sm rounded-md hover:bg-orange-100
                   {selectedFilter === filter ? 'bg-orange-400 text-white font-medium' : 'text-gray-700'}"
            on:click={() => handleFilterChange(filter)}
          >
            {filter}
          </button>
        {/each}
        {#if selectedFilter}
          <button
            class="mt-2 w-full text-left px-3 py-2 text-sm rounded-md bg-gray-100 text-gray-600 hover:bg-gray-200"
            on:click={clearFilters}
          >
            ล้างตัวกรองทั้งหมด
          </button>
        {/if}
      </div>
    </div>
  {/if}
</div>


    <!-- Categories -->
    <div class="flex gap-3 justify-center">
      {#each mainCategories as cat}
        <button
          class="px-6 py-2 rounded-full text-sm font-medium transition-all duration-200 hover:shadow-md flex-1 max-w-32
                 {cat === selected
            ? 'bg-orange-400 text-white shadow-lg transform scale-105'
            : 'bg-neutral-200 text-gray-800 hover:bg-neutral-300'}"
          on:click={() => handleCategoryChange(cat)}
          disabled={categoryLoading}
          aria-pressed={cat === selected}
        >
          {cat}
        </button>
      {/each}
    </div>

    <!-- Category Loading Indicator -->
    {#if categoryLoading}
      <div class="flex justify-center items-center py-4">
        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-orange-400"></div>
        <span class="ml-2 text-gray-600 text-sm">กำลังโหลดหมวดหมู่...</span>
      </div>
    {/if}

    <!-- Books Section -->
    {#if displayedPopular.length > 0}
      <div>
        <h2 class="text-2xl font-bold mb-3 kanit-semibold flex items-center gap-2">
          {getSectionTitle()}
          <span class="text-sm font-normal text-gray-500">({displayedPopular.length} เล่ม)</span>
        </h2>
        <!-- Grid Layout for Books -->
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
          {#each displayedPopular as book}
            <div
              class="cursor-pointer transform hover:scale-105 transition-transform duration-200"
              on:click={() => handleBookClick(book)}
              on:keydown={(e) => e.key === "Enter" && handleBookClick(book)}
              tabindex="0"
              role="button"
              aria-label={`ดูหนังสือ ${book.title}`}
            >
              <div class="relative">
                <img
                  src={book.cover}
                  alt={book.title}
                  class="w-full aspect-[3/4.2] object-cover rounded-md shadow hover:shadow-lg transition-shadow duration-200"
                  on:error={(e) => {
                    e.target.src =
                      "https://placehold.co/160x240/cccccc/666666?text=No+Image";
                  }}
                />
                <!-- Price Badge -->
                <div
                  class="absolute top-2 right-2 px-2 py-1 rounded-full text-xs font-bold flex items-center gap-1 shadow-sm"
                  class:bg-green-500={book.price === 0}
                  class:bg-orange-400={book.price > 0}
                  class:text-white={true}
                >
                  <img
                    src={SANPoint}
                    alt="Points"
                    class="w-3 h-3 object-contain"
                  />
                  <span>{formatPrice(book.price)}</span>
                </div>
              </div>
              <p
                class="mt-2 font-semibold text-sm md:text-base truncate"
              >
                {book.title}
              </p>
              <p class="text-xs text-gray-500 truncate">
                แต่งโดย {book.author || "ไม่ระบุ"}
              </p>
              <div class="flex items-center justify-between mt-1">
                <div class="flex items-center">
                  <div class="flex text-yellow-400 text-xs">
                    {#each Array(5) as _, i}
                      <span
                        class={i < Math.floor(book.rating || 0)
                          ? "text-yellow-400"
                          : "text-gray-300"}>★</span
                      >
                    {/each}
                  </div>
                  <span class="text-xs text-gray-500 ml-1"
                    >{(book.rating || 0).toFixed(1)}</span
                  >
                </div>
                <!-- Price Display -->
                <div
                  class="flex items-center gap-1 text-xs"
                  class:text-green-600={book.price === 0}
                  class:text-orange-600={book.price > 0}
                >
                  <img
                    src={SANPoint}
                    alt="Points"
                    class="w-3 h-3 object-contain opacity-70"
                  />
                </div>
              </div>
            </div>
          {/each}
        </div>
      </div>
    {:else}
      <div class="text-center py-8">
        <p class="text-gray-500">
          {searchQuery ? `ไม่พบผลลัพธ์สำหรับ "${searchQuery}"` : `ไม่พบหนังสือใน${getSectionTitle()}`}
        </p>
        {#if searchQuery}
          <button 
            class="mt-2 text-orange-500 hover:text-orange-600 text-sm"
            on:click={() => searchQuery = ""}
          >
            ล้างการค้นหา
          </button>
        {/if}
      </div>
    {/if}
  {/if}
</div>

<style>
  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }
</style>