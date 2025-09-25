<script>
  import { LogOut, Settings, Save, Loader } from "@lucide/svelte";
  import { onMount, onDestroy } from 'svelte';
  import { clearAuth } from "../lib/auth";
  import { getUserSettings, updateSetting } from "../lib/api.js"; // ✨ Import API functions
  import toast, { Toaster } from 'svelte-french-toast'; // ✨ Toast notifications

  function logout() {
    clearAuth();
    location.reload();
  }

  // Settings state
  let readingModeScroll = true;
  let darkModeOption = 'dark';
  let showDropdown = false;
  
  // ✨ Loading state
  let isLoading = true;

  // Close dropdown when clicking outside
  function handleClickOutside(event) {
    const dropdown = document.getElementById('dropdown');
    const button = document.getElementById('dropdown-button');
    
    if (dropdown && !dropdown.contains(event.target) && 
        button && !button.contains(event.target)) {
      showDropdown = false;
    }
  }

  // ✨ Load settings from server on mount
  onMount(async () => {
    document.addEventListener('click', handleClickOutside);
    
    try {
      // Load settings from server
      const response = await getUserSettings();
      const serverSettings = response.settings;
      
      // Update local state with server settings
      readingModeScroll = serverSettings.readingModeScroll ?? true;
      darkModeOption = serverSettings.darkModeOption ?? 'dark';
      
      // Apply theme
      setDarkMode(darkModeOption, false); // false = don't save to server
      
      console.log('🎉 Settings loaded from server:', serverSettings);
    } catch (error) {
      console.error('❌ Failed to load settings:', error);
      // Fallback to localStorage if server fails
      const savedTheme = localStorage.getItem('darkModePreference') || 'dark';
      setDarkMode(savedTheme, false);
    } finally {
      isLoading = false;
    }
    
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  });

  // ✨ Save setting to server with toast notifications
  async function saveSetting(key, value) {
    const savePromise = updateSetting(key, value);
    
    toast.promise(savePromise, {
      loading: 'กำลังบันทึก...',
      success: 'บันทึกสำเร็จ!',
      error: 'ไม่สามารถบันทึกได้'
    });

    try {
      await savePromise;
      console.log(`✅ ${key} saved:`, value);
    } catch (error) {
      console.error(`❌ Failed to save ${key}:`, error);
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
      if (prefersDark) {
        document.documentElement.classList.add("dark");
      } else {
        document.documentElement.classList.remove("dark");
      }
    }

    // Save to localStorage for immediate access
    localStorage.setItem('darkModePreference', option);
    
    // ✨ Save to server
    if (saveToServer) {
      saveSetting('darkModeOption', option);
    }
    
    console.log('🎨 Dark Mode selected:', option);
  }

  // ✨ Handle reading mode toggle with server sync
  async function handleReadingModeToggle() {
    readingModeScroll = !readingModeScroll;
    await saveSetting('readingModeScroll', readingModeScroll);
    console.log('📖 Reading Mode toggled:', readingModeScroll);
  }

  function toggleDropdown() {
    showDropdown = !showDropdown;
  }
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

<!-- ✨ Toast Container -->

<div class="min-h-screen bg-gray-50 dark:bg-gray-900 flex justify-center px-4 sm:px-6 lg:px-8 py-8">
  <div class="w-full bg-white dark:bg-gray-800 rounded-2xl shadow-md overflow-hidden relative">
    
    <!-- ✨ Loading overlay -->
    {#if isLoading}
      <div class="absolute inset-0 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm z-10 flex items-center justify-center">
        <div class="flex items-center gap-2 text-gray-600 dark:text-gray-300">
          <Loader class="w-5 h-5 animate-spin" />
          กำลังโหลดการตั้งค่า...
        </div>
      </div>
    {/if}

    <div class="border-b border-gray-200 dark:border-gray-700 px-6 py-6 flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold text-gray-900 dark:text-gray-100 font-['LINE_Seed_Sans_TH']">
          Creator Dashboard
        </h2>
        <p class="text-sm text-gray-500 dark:text-gray-400">ไปหน้าจัดการผู้สร้างหนังสือ</p>
      </div>
      <button class="text-gray-500 dark:text-gray-300 hover:text-gray-700 dark:hover:text-white transition-colors">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 rotate-180" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
      </button>
    </div>

    <!-- Settings List -->
    <div class="divide-y divide-gray-200 dark:divide-gray-700 relative">
      
      <!-- Reading Mode Scroll -->
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
            on:change={handleReadingModeToggle}
          />
          <div class="w-11 h-6 bg-gray-300 dark:bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:bg-indigo-500 transition-colors duration-200"></div>
          <div class="absolute left-0.5 top-0.5 size-5 bg-white dark:bg-gray-200 rounded-full transition-transform duration-200 peer-checked:translate-x-5"></div>
        </label>
      </div>

      <!-- Dark Mode Dropdown -->
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
            on:click|stopPropagation={toggleDropdown}
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
                    on:click={() => setDarkMode('light')}
                    class="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white transition-colors {darkModeOption === 'light' ? 'bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400' : ''}"
                  >
                    White
                  </button>
                </li>
                <li>
                  <button 
                    on:click={() => setDarkMode('dark')}
                    class="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white transition-colors {darkModeOption === 'dark' ? 'bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400' : ''}"
                  >
                    Dark
                  </button>
                </li>
                <li>
                  <button 
                    on:click={() => setDarkMode('system')}
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

      <!-- ✨ New Settings Section -->
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
            checked={true}
            disabled
          />
          <div class="w-11 h-6 bg-green-500 peer-focus:outline-none rounded-full peer transition-colors duration-200 opacity-75"></div>
          <div class="absolute left-0.5 top-0.5 size-5 bg-white rounded-full transition-transform duration-200 translate-x-5"></div>
        </label>
      </div>

      <!-- Logout Button -->
       <div class="flex items-center justify-between px-6 py-5">
        <div class="flex-1">
          <h3 class="text-base font-bold text-gray-900 dark:text-gray-100">Logout</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">Logout from your account</p>
        </div>
        <button 
          class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
          on:click={logout}
        >
          <LogOut class="w-4 h-4" />
          Logout
        </button>
      </div>
    </div>
  </div>
</div>