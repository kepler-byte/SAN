<script>
  import { House, Search, CircleAlert, Bookmark, Filter, Loader } from "@lucide/svelte";
  import { createEventDispatcher, onMount, onDestroy } from "svelte";
import { getAllBooks, getCurrentUser, getBookCover, getPersonalizedRecommendations } from "../lib/api.js";
  import SANPoint from "../assets/SAN_Point_White.svg";

  const dispatch = createEventDispatcher();

  // User state
  let username = "User";
  let points = 0;

  // Loading & error
  let loading = true;
  let error = null;

  // Search & categories
  let searchQuery = "";
  let mainCategories = ["ยอดนิยม", "มาใหม่", "แนะนำสำหรับคุณ", "ทั้งหมด"];
  let filterCategories = ["ความรู้", "นิยาย", "มังงะ", "ศิลปะ", "วิทยาศาสตร์", "ประวัติศาสตร์", "ธุรกิจ", "การศึกษา", "เทคโนโลยี", "สุขภาพ", "การเงิน", "จิตวิทยา", "อื่นๆ"];
  let selected = "ยอดนิยม";
  let selectedFilter = null;
  let showFilterDropdown = false;

  // Book data
  let allBooks = [];
  let categoryBooks = [];
  let categoryLoading = false;

  // Cover image cache
  let coverObjectUrls = new Map();
  let objectUrlsForCleanup = [];

  // Reactive derived data
  $: filteredBooks = (() => {
    let books = selected === "ทั้งหมด" ? allBooks : categoryBooks;

    if (selectedFilter) {
      books = books.filter(book => book.category === selectedFilter);
    }

    if (searchQuery.trim()) {
      books = books.filter((book) => {
        const titleMatch = book.title?.toLowerCase().includes(searchQuery.toLowerCase());
        const authorMatch = (book.author || "").toLowerCase().includes(searchQuery.toLowerCase());
        return titleMatch || authorMatch;
      });
    }

    return books;
  })();

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
      coverUrl: coverObjectUrls.get(book.id) || getPlaceholderImage(),
      isLoadingCover: false
    }));

  onDestroy(() => {
    objectUrlsForCleanup.forEach(url => URL.revokeObjectURL(url));
    coverObjectUrls.clear();
  });

  function getPlaceholderImage() {
    return `https://placehold.co/160x240/cccccc/666666?text=No+Image`;
  }

  async function loadBookCover(bookId) {
    if (coverObjectUrls.has(bookId)) return;
    try {
      const blob = await getBookCover(bookId);
      if (blob) {
        const objectUrl = URL.createObjectURL(blob);
        coverObjectUrls.set(bookId, objectUrl);
        objectUrlsForCleanup.push(objectUrl);
        coverObjectUrls = coverObjectUrls;
      }
    } catch (error) {
      console.error(`Failed to load cover for book ${bookId}:`, error);
      coverObjectUrls.set(bookId, getPlaceholderImage());
      coverObjectUrls = coverObjectUrls;
    }
  }

  $: {
    if (displayedPopular.length > 0) {
      displayedPopular.forEach(book => {
        if (book.has_cover && !coverObjectUrls.has(book.id)) {
          loadBookCover(book.id);
        }
      });
    }
  }

  onMount(async () => {
    try {
      loading = true;
      const userData = await getCurrentUser();
      username = userData.username || userData.name || "User";
      points = userData.points || 0;

      const booksResponse = await getAllBooks(0, 50);
      allBooks = Array.isArray(booksResponse) ? booksResponse : [];
      categoryBooks = allBooks;
    } catch (err) {
      console.error("Failed to load data:", err);
      error = err.message || "ไม่สามารถโหลดข้อมูลได้";
      allBooks = [];
      categoryBooks = [];
    } finally {
      loading = false;
    }
  });

  // ✅ หมวดหมู่ต่าง ๆ รวม “แนะนำสำหรับคุณ”
  async function handleCategoryChange(category) {
    if (selected === category) return;
    selected = category;
    selectedFilter = null;
    categoryLoading = true;

    try {
      if (category === "ทั้งหมด" || category === "ยอดนิยม" || category === "มาใหม่") {
        categoryBooks = allBooks;
      } else if (category === "แนะนำสำหรับคุณ") {
const personalizedBooks = await getPersonalizedRecommendations();
        categoryBooks = Array.isArray(personalizedBooks) ? personalizedBooks : [];
      } else {
        categoryBooks = allBooks;
      }
    } catch (err) {
      console.error("Failed to load category:", err);
      categoryBooks = [];
    } finally {
      categoryLoading = false;
    }
  }

  function handleFilterChange(filter) {
    selectedFilter = selectedFilter === filter ? null : filter;
    showFilterDropdown = false;
  }

  function clearFilters() {
    selectedFilter = null;
    searchQuery = "";
    showFilterDropdown = false;
  }

  function handleBookClick(book) {
    const bookWithPrice = { ...book, price: book.price ?? 0 };
    sessionStorage.setItem("selectedBook", JSON.stringify(bookWithPrice));
    dispatch("navigate", "bookpreview");
  }

  function formatPrice(price) {
    return price === undefined || price === null || price === 0 ? "ฟรี" : `${price}`;
  }

  function getSectionTitle() {
    let title = "";
    switch (selected) {
      case "ยอดนิยม": title = "หนังสือยอดนิยม"; break;
      case "มาใหม่": title = "หนังสือใหม่"; break;
      case "แนะนำสำหรับคุณ": title = "หนังสือแนะนำสำหรับคุณ"; break;
      case "ทั้งหมด": title = "หนังสือทั้งหมด"; break;
      default: title = selected;
    }
    if (selectedFilter) title += ` - ${selectedFilter}`;
    return title;
  }

  function handleImageError(event, book) {
    console.log(`Image failed to load for book: ${book.title}`);
    event.target.src = getPlaceholderImage();
  }
</script>

<!-- HEADER -->
<div class="p-6 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
  <div class="flex items-center gap-3">
    <div class="w-8 h-8 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
      <House class="w-4 h-4 text-gray-600 dark:text-gray-300" />
    </div>
    <h1 class="text-lg font-semibold text-gray-900 dark:text-gray-100">หน้าหลัก</h1>
  </div>
</div>

<!-- MAIN CONTENT -->
<div class="min-h-screen bg-white px-6 py-5 space-y-6">
  {#if loading}
    <div class="absolute inset-0 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm z-10 flex items-center justify-center">
      <div class="flex items-center gap-2 text-gray-600 dark:text-gray-300">
        <Loader class="w-5 h-5 animate-spin" /> กำลังโหลดข้อมูล...
      </div>
    </div>
  {:else if error}
    <div class="bg-red-50 border border-red-200 rounded-lg p-4 flex">
      <CircleAlert class="w-6 h-6 text-red-600" />
      <p class="ml-3 text-sm text-red-800">เกิดข้อผิดพลาด: {error}</p>
    </div>
  {:else}
    <!-- USER HEADER -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <img src="https://placehold.co/40x40" class="w-10 h-10 rounded-lg shadow" alt="Profile" />
        <div>
          <p class="text-sm text-gray-700">สวัสดีตอนเช้า</p>
          <p class="text-lg font-bold">{username}</p>
        </div>
      </div>
      <div class="bg-orange-400 text-white px-4 py-2 rounded-full font-bold text-sm flex items-center gap-1">
        <span>{points}</span>
        <img src={SANPoint} alt="SAN Logo" class="w-4 h-4 object-contain" />
      </div>
    </div>

    <!-- SEARCH & FILTER -->
    <div class="relative">
      <div class="flex items-center justify-between bg-white px-3 py-2 rounded-lg shadow">
        <input type="text" placeholder="ค้นหาหนังสือของคุณ" class="flex-1 text-sm text-gray-500 focus:outline-none"
          bind:value={searchQuery} />
        <button class="p-2 bg-orange-400 rounded-md" on:click={() => showFilterDropdown = !showFilterDropdown}>
          <Filter class="w-4 h-4 text-white" />
        </button>
      </div>

      {#if showFilterDropdown}
        <div class="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-10 p-2">
          {#each filterCategories as filter}
            <button
              class="w-full text-left px-3 py-2 text-sm rounded-md hover:bg-orange-100
              {selectedFilter === filter ? 'bg-orange-400 text-white font-medium' : 'text-gray-700'}"
              on:click={() => handleFilterChange(filter)}>
              {filter}
            </button>
          {/each}
          {#if selectedFilter}
            <button class="mt-2 w-full px-3 py-2 text-sm rounded-md bg-gray-100 text-gray-600 hover:bg-gray-200"
              on:click={clearFilters}>
              ล้างตัวกรองทั้งหมด
            </button>
          {/if}
        </div>
      {/if}
    </div>

    <!-- CATEGORY BUTTONS -->
    <div class="flex gap-3 justify-center">
      {#each mainCategories as cat}
        <button
          class="px-6 py-2 rounded-full text-sm font-medium transition-all flex-1 max-w-32
          {cat === selected ? 'bg-orange-400 text-white shadow-lg scale-105' : 'bg-neutral-200 text-gray-800 hover:bg-neutral-300'}"
          on:click={() => handleCategoryChange(cat)} disabled={categoryLoading}>
          {cat}
        </button>
      {/each}
    </div>

    {#if categoryLoading}
      <div class="flex justify-center items-center py-4">
        <Loader class="w-5 h-5 animate-spin text-orange-400" />
        <span class="ml-2 text-sm text-gray-600">กำลังโหลดหมวดหมู่...</span>
      </div>
    {/if}

    <!-- BOOKS GRID -->
    {#if displayedPopular.length > 0}
      <div>
        <h2 class="text-2xl font-bold mb-3 flex items-center gap-2">
          {getSectionTitle()} <span class="text-sm text-gray-500">({displayedPopular.length} เล่ม)</span>
        </h2>
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
          {#each displayedPopular as book (book.id)}
            <div class="cursor-pointer transform hover:scale-105 transition-transform duration-200"
              on:click={() => handleBookClick(book)}>
              <div class="relative">
                {#if book.has_cover && !coverObjectUrls.has(book.id)}
                  <div class="w-full aspect-[3/4.2] bg-gray-200 rounded-md flex items-center justify-center">
                    <Loader class="w-5 h-5 animate-spin text-orange-400" />
                  </div>
                {:else}
                  <img src={book.has_cover && coverObjectUrls.has(book.id)
                      ? coverObjectUrls.get(book.id)
                      : getPlaceholderImage()}
                    alt={book.title}
                    class="w-full aspect-[3/4.2] object-cover rounded-md shadow"
                    on:error={(e) => handleImageError(e, book)} />
                {/if}

                <div
                  class="absolute top-2 right-2 px-2 py-1 rounded-full text-xs font-bold flex items-center gap-1 shadow-sm
                  {book.price === 0 ? 'bg-green-500' : 'bg-orange-400'} text-white">
                  <span>{formatPrice(book.price)}</span>
                  <img src={SANPoint} class="w-3 h-3 object-contain" />
                </div>
              </div>
              <p class="mt-2 font-semibold text-sm truncate">{book.title}</p>
              <p class="text-xs text-gray-500 truncate">แต่งโดย {book.author || "ไม่ระบุ"}</p>
            </div>
          {/each}
        </div>
      </div>
    {:else}
      <div class="text-center py-8 text-gray-500">
        {#if selected === "แนะนำสำหรับคุณ"}
          คุณยังไม่เริ่มอ่านหนังสือใด ๆ
        {:else if searchQuery}
          ไม่พบผลลัพธ์สำหรับ "{searchQuery}"
          <button class="mt-2 text-orange-500 hover:text-orange-600 text-sm" on:click={() => searchQuery = ""}>
            ล้างการค้นหา
          </button>
        {:else}
          ไม่พบหนังสือใน {getSectionTitle()}
        {/if}
      </div>
    {/if}
  {/if}
</div>
