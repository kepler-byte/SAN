<script>
  import { LogOut, Settings, Save, Loader, BookOpenCheck, ChevronUp, CircleDollarSign, Download, MessageCircle, Plane, Plus, X, Undo2 } from "@lucide/svelte";
  import { onMount, onDestroy } from 'svelte';
  import { clearAuth } from "../lib/auth";
  import { getUserSettings, updateSetting, getCreatorStats, getSalesHistory, getCreatorBooks, getCurrentUser, getBookCover } from "../lib/api.js";
  import { Toaster, toast } from 'svelte-sonner'
  import { Chart, LineController, LineElement, PointElement, LinearScale, CategoryScale, Title, Tooltip, Legend } from 'chart.js';

  Chart.register(LineController, LineElement, PointElement, LinearScale, CategoryScale, Title, Tooltip, Legend);

  // State สำหรับ modal โปรไฟล์
  let showProfileModal = $state(false);
  let showCancelConfirm = $state(false);

  let coverObjectUrls = $state(new Map()); // Map book ID to object URL
  let objectUrlsForCleanup = []; // Array to track all created URLs for cleanup

  // State สำหรับ Creator Dashboard
  let showCreatorDashboard = $state(false);

  // Profile data
  let profile = $state({
    avatar: "https://i.pravatar.cc/150?img=12",
    name: "",
    username: "",
    email: ""
  });

  function saveProfile() {
    console.log("Profile saved:", profile);
    showProfileModal = false;
    toast.success("บันทึกโปรไฟล์สำเร็จ");
  }

  function cancelProfile() {
    showCancelConfirm = true;
  }

  function confirmCancel() {
    showCancelConfirm = false;
    showProfileModal = false;
  }
  
  function logout() {
    clearAuth();
    location.reload();
  }

  // Component state
  let readingModeScroll = $state(true);
  let darkModeOption = $state('light');
  let showDropdown = $state(false);
  let isLoading = $state(true);
  let autoSaveEnabled = $state(true);

  function handleAutoSaveToggle(event) {
    autoSaveEnabled = event.target.checked;
    saveSetting('autoSaveEnabled', autoSaveEnabled);
  }

  function handleReadingModeToggle(event) {
    readingModeScroll = event.target.checked;
    saveSetting('readingModeScroll', readingModeScroll);
  }

  function handleClickOutside(event) {
    const dropdown = document.getElementById('dropdown');
    const button = document.getElementById('dropdown-button');
    if (dropdown && !dropdown.contains(event.target) && button && !button.contains(event.target)) {
      showDropdown = false;
    }
  }

  onMount(() => {
    document.addEventListener('click', handleClickOutside);

    (async () => {
      try {
        // Load user settings
        const response = await getUserSettings();
        const serverSettings = response.settings;
        readingModeScroll = serverSettings.readingModeScroll ?? true;
        darkModeOption = serverSettings.darkModeOption ?? 'dark';
        autoSaveEnabled = serverSettings.autoSaveEnabled ?? true;
        setDarkMode(darkModeOption, false);

        // Load user info for profile
        const userInfo = await getCurrentUser();
        profile.name = userInfo.full_name || userInfo.username;
        profile.username = userInfo.username;
        profile.email = userInfo.email;
        
        console.log('Settings loaded from server:', serverSettings);
      } catch (error) {
        console.error('Failed to load settings:', error);
        const savedTheme = localStorage.getItem('darkModePreference') || 'dark';
        setDarkMode(savedTheme, false);
      } finally {
        isLoading = false;
      }
    })();

    return () => document.removeEventListener('click', handleClickOutside);
  });

  async function saveSetting(key, value) {
    if (!autoSaveEnabled && key !== 'autoSaveEnabled') {
      console.log(`Auto Save ปิด → ข้ามการบันทึก ${key}`);
      return;
    }

    const savePromise = updateSetting(key, value);
    toast.promise(savePromise, {
      loading: 'กำลังบันทึก...',
      success: 'บันทึกสำเร็จ!',
      error: 'ไม่สามารถบันทึกได้'
    });

    try {
      await savePromise;
      console.log(`${key} saved:`, value);
    } catch (error) {
      console.error(`Failed to save ${key}:`, error);
    }
  }

  function setDarkMode(option, saveToServer = true) {
    darkModeOption = option;
    showDropdown = false;

    if (option === 'dark') {
      document.documentElement.classList.add("dark");
    } else if (option === 'light') {
      document.documentElement.classList.remove("dark");
    } else if (option === 'system') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      document.documentElement.classList.toggle('dark', prefersDark);
    }

    localStorage.setItem('darkModePreference', option);
    if (saveToServer) saveSetting('darkModeOption', option);
  }

  function toggleDropdown() {
    showDropdown = !showDropdown;
  }

  // Creator Dashboard State
  let creator = $state({
    name: "",
    username: "",
    avatar: "/avatar.png",
  });

  let activeChart = $state(0);
  let stats = $state([
    { label: "Total Follower", value: 0 },
    { label: "Total Reader", value: 0 },
    { label: "Total Like", value: 0 },
    { label: "Total Sales", value: 0 },
  ]);

  let salesDatasets = $state([[], [], [], []]);
  let books = $state([]);
  let chartCanvas;
  let chart;
  let dashboardLoading = $state(false);

  function renderChart(index) {
    if (!showCreatorDashboard || !chartCanvas) return;
    
    const sales = salesDatasets[index] || [];
    if (!chart) {
      chart = new Chart(chartCanvas, {
        type: 'line',
        data: {
          labels: sales.map(s => s.month),
          datasets: [{
            label: 'Sales',
            data: sales.map(s => s.value),
            borderColor: '#f97316',
            backgroundColor: 'rgba(249, 115, 22, 0.2)',
            borderWidth: 2,
            pointRadius: 4,
            pointBackgroundColor: '#f97316',
            tension: 0.3,
            fill: true,
          }]
        },
        options: {
          responsive: true,
          animation: { duration: 600 },
          plugins: {
            legend: { display: false },
            tooltip: { mode: 'index', intersect: false }
          },
          scales: {
            x: { grid: { display: false } },
            y: { beginAtZero: true }
          }
        }
      });
    } else {
      chart.data.labels = sales.map(s => s.month);
      chart.data.datasets[0].data = sales.map(s => s.value);
      chart.update();
    }
  }

  $effect(() => {
    if (chart && showCreatorDashboard) {
      renderChart(activeChart);
    }
  });

  $effect(() => {
    if (showCreatorDashboard && chartCanvas) {
      setTimeout(() => renderChart(activeChart), 100);
    }
  });

  async function openCreatorDashboard() {
    showCreatorDashboard = true;
    dashboardLoading = true;

    try {
      // Load creator stats
      const statsData = await getCreatorStats();
      stats = [
        { label: "Total Follower", value: statsData.total_followers },
        { label: "Total Reader", value: statsData.total_readers },
        { label: "Total Like", value: statsData.total_likes },
        { label: "Total Sales", value: statsData.total_sales },
      ];

      // Load sales history (last 6 months for each chart)
      const salesData = await getSalesHistory(6);
      salesDatasets = [salesData, salesData, salesData, salesData];

      // Load creator's books
      const booksData = await getCreatorBooks(0, 20);
      books = booksData.map(book => ({
        id: book.id,
        title: book.title,
        price: book.price,
        pages: book.total_readers,
        comments: book.total_comments
      }));

      // Set creator info
      const userInfo = await getCurrentUser();
      creator.name = userInfo.full_name || userInfo.username;

    } catch (error) {
      console.error('Failed to load creator dashboard:', error);
      toast.error('ไม่สามารถโหลดข้อมูล Creator Dashboard ได้');
    } finally {
      dashboardLoading = false;
    }
  }

  function closeCreatorDashboard() {
    showCreatorDashboard = false;
    if (chart) {
      chart.destroy();
      chart = null;
    }
  }

  // Clean up object URLs when component is destroyed
  onDestroy(() => {
    objectUrlsForCleanup.forEach(url => {
      URL.revokeObjectURL(url);
    });
    coverObjectUrls.clear();
  });

  // Function to get placeholder image
  function getPlaceholderImage() {
    return `https://images.unsplash.com/photo-${Math.random().toString(36).substr(2, 9)}?w=400&h=600&fit=crop`;
  }

  // Function to load cover image for a book
  async function loadBookCover(bookId) {
    if (coverObjectUrls.has(bookId)) {
      return;
    }

    try {
      const blob = await getBookCover(bookId);
      if (blob) {
        const objectUrl = URL.createObjectURL(blob);
        const newMap = new Map(coverObjectUrls);
        newMap.set(bookId, objectUrl);
        coverObjectUrls = newMap;
        objectUrlsForCleanup.push(objectUrl);
        console.log(`Cover loaded for book ${bookId}`);
      }
    } catch (error) {
      console.error(`Failed to load cover for book ${bookId}:`, error);
      const newMap = new Map(coverObjectUrls);
      newMap.set(bookId, getPlaceholderImage());
      coverObjectUrls = newMap;
    }
  }

  // Load covers for visible books in Creator Dashboard
  $effect(() => {
    if (books.length > 0 && showCreatorDashboard) {
      console.log(`Loading covers for ${books.length} books`);
      books.forEach(book => {
        if (!coverObjectUrls.has(book.id)) {
          loadBookCover(book.id);
        }
      });
    }
  });
  
</script>

<!-- Header -->
<div class="p-6 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
    <div class="flex items-center gap-3">
        <div class="w-8 h-8 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
            <Settings class="w-4 h-4 text-gray-600 dark:text-gray-300" />
        </div>
        <h1 class="text-lg font-semibold text-gray-900 dark:text-gray-100">หน้าการตั้งค่า</h1>
    </div>
</div>

<div class="bg-gray-50 dark:bg-gray-900 flex justify-center px-4 py-8 sm:px-6 lg:px-8" style="height: calc(100vh - 88px);">
  <div class="w-full bg-white dark:bg-gray-800 rounded-2xl shadow-md relative overflow-hidden" style="height: 100%;">
    
    {#if isLoading}
      <div class="absolute inset-0 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm z-10 flex items-center justify-center">
        <div class="flex items-center gap-2 text-gray-600 dark:text-gray-300">
          <Loader class="w-5 h-5 animate-spin" />
          กำลังโหลดการตั้งค่า...
        </div>
      </div>
    {/if}

    <!-- Main Settings Container -->
    <div class="settings-container" class:slide-out={showCreatorDashboard}>
      <div class="border-b border-gray-200 dark:border-gray-700 px-6 py-6 flex items-center justify-between">
        <div>
          <h2 class="text-xl font-bold text-gray-900 dark:text-gray-100 font-['LINE_Seed_Sans_TH']">
            Creator Dashboard
          </h2>
          <p class="text-sm text-gray-500 dark:text-gray-400">ไปหน้าจัดการผู้สร้างหนังสือ</p>
        </div>
        <button 
          class="text-gray-500 dark:text-gray-300 hover:text-gray-700 dark:hover:text-white transition-colors"
          onclick={openCreatorDashboard}
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 rotate-180" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
          </svg>
        </button>
      </div>

      <div class="divide-y divide-gray-200 dark:divide-gray-700 relative">
        
        <div class="flex items-center justify-between px-6 py-5">
          <div class="flex-1">
            <h3 class="text-base font-bold text-gray-900 dark:text-gray-100">
              Reading Mode
            </h3>
            <p class="text-sm text-gray-500 dark:text-gray-400">Scroll-based reading experience</p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input 
              type="checkbox" 
              class="sr-only peer" 
              bind:checked={readingModeScroll} 
              onchange={handleReadingModeToggle}
            />
            <div class="w-11 h-6 bg-gray-300 dark:bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:bg-indigo-500 transition-colors duration-200"></div>
            <div class="absolute left-0.5 top-0.5 size-5 bg-white dark:bg-gray-200 rounded-full transition-transform duration-200 peer-checked:translate-x-5"></div>
          </label>
        </div>

        <div class="flex items-center justify-between px-6 py-5 relative overflow-visible">
          <div class="flex-1">
            <h3 class="text-base font-bold text-gray-900 dark:text-gray-100">
              Dark Mode
            </h3>
            <p class="text-sm text-gray-500 dark:text-gray-400">เลือกโหมดสีของเว็บ</p>
          </div>
          <div class="relative">
            <button 
              id="dropdown-button"
              onclick={(e) => { e.stopPropagation(); toggleDropdown(); }}
              type="button"
              class="bg-gray- text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg px-3 py-2 text-sm font-medium inline-flex items-center transition-colors"
            >
              {darkModeOption === 'light' ? 'White' : darkModeOption === 'dark' ? 'Dark' : 'System'}
            </button>

            {#if showDropdown}
              <div id="dropdown" class="z-50 absolute end-0 mt-2 bg-white divide-y divide-gray-100 rounded-lg shadow-lg border border-gray-200 w-44 dark:bg-gray-700 dark:border-gray-600 dark:divide-gray-600">
                <ul class="py-2 text-sm text-gray-700 dark:text-gray-200">
                  <li>
                    <button 
                      onclick={() => setDarkMode('light')}
                      class="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white transition-colors {darkModeOption === 'light' ? 'bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400' : ''}"
                    >
                      White
                    </button>
                  </li>
                  <li>
                    <button 
                      onclick={() => setDarkMode('dark')}
                      class="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white transition-colors {darkModeOption === 'dark' ? 'bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400' : ''}"
                    >
                      Dark
                    </button>
                  </li>
                  <li>
                    <button 
                      onclick={() => setDarkMode('system')}
                      class="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white transition-colors {darkModeOption === 'system' ? 'bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400' : ''}"
                    >
                      System
                    </button>
                  </li>
                </ul>
              </div>
            {/if}
          </div>
        </div>

        <div class="flex items-center justify-between px-6 py-5">
          <div class="flex-1">
            <h3 class="text-base font-bold text-gray-900 dark:text-gray-100">
              Auto Save
            </h3>
            <p class="text-sm text-gray-500 dark:text-gray-400">บันทึกการตั้งค่าอัตโนมัติ</p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input 
              type="checkbox" 
              class="sr-only peer" 
              bind:checked={autoSaveEnabled}
              onchange={handleAutoSaveToggle}
            />
            <div class="w-11 h-6 bg-gray-300 dark:bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:bg-green-500 transition-colors duration-200"></div>
            <div class="absolute left-0.5 top-0.5 size-5 bg-white rounded-full transition-transform duration-200 peer-checked:translate-x-5"></div>
          </label>
        </div>

        <div class="flex items-center justify-between px-6 py-5">
          <div class="flex-1">
            <h3 class="text-base font-bold text-gray-900 dark:text-gray-100">
              จัดการโปรไฟล์
            </h3>
            <p class="text-sm text-gray-500 dark:text-gray-400">แก้ไขข้อมูลโปรไฟล์ของคุณ</p>
          </div>
          <button
            class="bg-indigo-500 hover:bg-indigo-600 text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
            onclick={() => showProfileModal = true}
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
            ไปที่โปรไฟล์
          </button>
        </div>

        <div class="flex items-center justify-between px-6 py-5">
          <div class="flex-1">
            <h3 class="text-base font-bold text-gray-900 dark:text-gray-100">Logout</h3>
            <p class="text-sm text-gray-500 dark:text-gray-400">Logout from your account</p>
          </div>
          <button 
            class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
            onclick={logout}
          >
            <LogOut class="w-4 h-4" />
            Logout
          </button>
        </div>
      </div>
    </div>

    <!-- Creator Dashboard Container -->
    <div class="dashboard-container" class:slide-in={showCreatorDashboard}>
      {#if dashboardLoading}
        <div class="absolute inset-0 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm z-10 flex items-center justify-center">
          <div class="flex items-center gap-2 text-gray-600 dark:text-gray-300">
            <Loader class="w-5 h-5 animate-spin" />
            กำลังโหลดข้อมูล...
          </div>
        </div>
      {/if}

      <div class="p-4 md:p-8 max-w-5xl mx-auto">
        
        <!-- Close Button -->
        <div class="flex justify-start gap-4 items-center mb-6">
          <button 
            class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            onclick={closeCreatorDashboard}
          >
            <Undo2 class="w-6 h-6 text-gray-600 dark:text-gray-300" />
          </button>
          <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Creator Dashboard</h2>
        </div>

        <!-- Profile -->
        <div class="flex flex-col items-center mt-6">
          <img src={creator.avatar} alt="avatar" class="w-20 h-20 rounded-full shadow" />
          <h2 class="mt-2 text-lg font-bold text-gray-900 dark:text-gray-100">{creator.name}</h2>
          <p class="text-sm text-gray-500 dark:text-gray-400">{creator.username}</p>
          <button
            class="group w-full mt-4 px-6 py-4 rounded-xl bg-orange-500 text-white font-semibold flex items-center justify-center gap-2
                   transform transition duration-200 ease-out hover:-translate-y-1 hover:shadow-lg active:scale-95 focus:outline-none focus:ring-2 focus:ring-orange-300"
          >
            <Plus class="w-5 h-5 inline-block mr-2 transition-transform duration-200 ease-out group-hover:translate-x-1" />
            เพิ่มหนังสือใหม่
          </button>
        </div>

        <!-- Overview -->
        <section class="mt-8">
          <h3 class="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">Overview</h3>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            {#each stats as s}
              <div class="group bg-white dark:bg-gray-700 shadow rounded-xl p-4 relative text-left transform transition-transform duration-300 ease-out hover:-translate-y-2 hover:scale-105 hover:shadow-2xl cursor-pointer">
                <div class="absolute top-3 right-3">
                  <div class="w-10 h-10 bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded-lg flex items-center justify-center transform transition duration-400 group-hover:-translate-y-1 group-hover:rotate-12 shadow-sm">
                    <Plane class="w-4 h-4" />
                  </div>
                </div>
                <p class="font-semibold text-gray-700 dark:text-gray-300">{s.label}</p>
                <p class="text-2xl font-bold mt-2 text-gray-900 dark:text-gray-100">{s.value.toLocaleString()}</p>
              </div>
            {/each}
          </div>
        </section>

        <!-- Chart -->
        <section class="mt-8">
          <div class="flex justify-between items-center">
            <h3 class="text-xl font-bold text-gray-900 dark:text-gray-100">Sales</h3>
            <button
              class="rounded-full bg-orange-500 text-white text-sm font-semibold px-4 py-2
                     transform transition duration-200 ease-out hover:-translate-y-1 hover:scale-105 hover:shadow-lg
                     hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-orange-300 group"
            >
              <Download class="w-4 h-4 inline-block mr-1 transition-transform duration-200 ease-out group-hover:-translate-y-1" />
              Export to .xlsx
            </button>
          </div>

          <div class="mt-3 w-full bg-white dark:bg-gray-700 rounded-lg shadow-sm p-4 md:p-6">
            <canvas bind:this={chartCanvas} class="w-full h-64"></canvas>
          </div>

          <div class="flex justify-center gap-2 mt-4">
            {#each [0, 1, 2, 3] as i}
              <button
                class="w-8 h-8 rounded-full flex items-center justify-center transform transition-all duration-300
                       hover:-translate-y-1 hover:scale-110 hover:shadow-lg
                       {i === activeChart ? 'bg-orange-500 text-white ring-2 ring-orange-200' : 'bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-200'}"
                onclick={() => activeChart = i}
              >
                {i + 1}
              </button>
            {/each}
          </div>
        </section>

        <!-- Book Manager -->
        <section class="mt-8">
          <h3 class="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">Book Manager</h3>
          <div class="space-y-4">
            {#each books as b (b.id)}
              <div class="flex items-center bg-white dark:bg-gray-700 rounded-xl p-4 shadow transform transition-all duration-300 hover:-translate-y-1 hover:shadow-lg cursor-pointer">
                {#if coverObjectUrls.has(b.id)}
                  <img 
                    src={coverObjectUrls.get(b.id)} 
                    alt={b.title}
                    class="w-16 h-20 rounded-md flex-shrink-0 object-cover"
                  />
                {:else}
                  <div class="w-16 h-20 bg-gradient-to-br from-pink-400 to-purple-500 rounded-md flex-shrink-0 flex items-center justify-center">
                    <Loader class="w-6 h-6 text-white animate-spin" />
                  </div>
                {/if}

                <div class="ml-4 flex-1">
                  <div class="flex items-start justify-between gap-4">
                    <h4 class="font-bold text-gray-900 dark:text-gray-100">{b.title}</h4>
                    <span class="bg-green-200 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs px-2 py-1 rounded">สาธารณะ</span>
                  </div>

                  <div class="flex gap-4 text-sm mt-2 text-gray-600 dark:text-gray-400 items-center">
                    <span class="flex items-center gap-1">
                      <CircleDollarSign class="w-4 h-4" />
                      {b.price}
                    </span>
                    <span class="flex items-center gap-1">
                      <BookOpenCheck class="w-4 h-4" />
                      {b.pages}
                    </span>
                    <span class="flex items-center gap-1">
                      <MessageCircle class="w-4 h-4" />
                      {b.comments}
                    </span>
                  </div>
                </div>
              </div>
            {/each}
          </div>
        </section>
      </div>
    </div>

    <!-- Profile Modal -->
    {#if showProfileModal}
      <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8 w-full max-w-2xl mx-4">
          <h2 class="text-xl font-bold mb-6 text-gray-900 dark:text-gray-100">โปรไฟล์ของฉัน</h2>
          
          <div class="flex items-center gap-6">
            <img src={profile.avatar} alt="avatar" class="w-20 h-20 rounded-full object-cover" />
            <div class="space-y-2 flex-1">
              <div>
                <label class="block text-sm text-gray-500 dark:text-gray-400">ชื่อ</label>
                <input
                  type="text"
                  bind:value={profile.name}
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 mt-1 bg-gray-50 dark:bg-gray-700 dark:text-gray-100"
                />
              </div>
              <div>
                <label class="block text-sm text-gray-500 dark:text-gray-400">Username</label>
                <input
                  type="text"
                  bind:value={profile.username}
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 mt-1 bg-gray-50 dark:bg-gray-700 dark:text-gray-100"
                />
              </div>
              <div>
                <label class="block text-sm text-gray-500 dark:text-gray-400">Email</label>
                <input
                  type="email"
                  bind:value={profile.email}
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 mt-1 bg-gray-50 dark:bg-gray-700 dark:text-gray-100"
                />
              </div>
            </div>
          </div>

          <div class="mt-8 flex justify-end gap-3">
            <button 
              class="px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-lg"
              onclick={cancelProfile}
            >
              ยกเลิก
            </button>
            <button 
              class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg"
              onclick={saveProfile}
            >
              บันทึก
            </button>
          </div>
        </div>
      </div>
    {/if}

    <!-- Cancel Confirm Modal -->
    {#if showCancelConfirm}
      <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 w-full max-w-md mx-4">
          <h3 class="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">
            คุณแน่ใจหรือไม่?
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            ถ้าไม่บันทึก ข้อมูลที่แก้ไขจะไม่ถูกบันทึก
          </p>

          <div class="mt-6 flex justify-end gap-3">
            <button 
              class="px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-lg"
              onclick={() => showCancelConfirm = false}
            >
              กลับไปแก้ไข
            </button>
            <button 
              class="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg"
              onclick={confirmCancel}
            >
              ไม่บันทึก
            </button>
          </div>
        </div>
      </div>
    {/if}
  </div>
</div>
<style>
  .settings-container {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    overflow-y: auto;
    transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    transform: translateX(0);
  }

  .settings-container.slide-out {
    transform: translateX(-100%);
  }

  .dashboard-container {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    overflow-y: auto;
    background: white;
    transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    transform: translateX(100%);
  }

  .dashboard-container.slide-in {
    transform: translateX(0);
  }

  /* Dark mode support */
  :global(.dark) .dashboard-container {
    background: rgb(31, 41, 55);
  }
</style>