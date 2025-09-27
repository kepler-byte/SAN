<script>
  import { LogOut, Settings, Save, Loader } from "@lucide/svelte";
  import { onMount } from 'svelte';
  import { clearAuth } from "../lib/auth";
  import { getUserSettings, updateSetting } from "../lib/api.js";
  import toast from 'svelte-french-toast';

  // 👉 state สำหรับ modal โปรไฟล์
  let showProfileModal = false;
  let showCancelConfirm = false;

  // mock data
  let profile = {
    avatar: "https://i.pravatar.cc/150?img=12",
    name: "John Doe",
    username: "johndoe",
    email: "johndoe@gmail.com"
  };

  function saveProfile() {
    console.log("Profile saved:", profile);
    showProfileModal = false;
  }

  function cancelProfile() {
    // โชว์ popup ยืนยันก่อนปิด
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
  let readingModeScroll = true;
  let darkModeOption = 'light'; // default theme
  let showDropdown = false;
  let isLoading = true;

  // เพิ่มตัวแปร state
  let autoSaveEnabled = true;

  // ✅ toggle โดยอิงค่าจาก event.target.checked
  function handleAutoSaveToggle(event) {
    autoSaveEnabled = event.target.checked;
    saveSetting('autoSaveEnabled', autoSaveEnabled);
  }

  function handleReadingModeToggle(event) {
    readingModeScroll = event.target.checked;
    saveSetting('readingModeScroll', readingModeScroll);
  }

  // Close dropdown when clicking outside
  function handleClickOutside(event) {
    const dropdown = document.getElementById('dropdown');
    const button = document.getElementById('dropdown-button');
    if (dropdown && !dropdown.contains(event.target) && button && !button.contains(event.target)) {
      showDropdown = false;
    }
  }

  // Load user settings on mount
  onMount(() => {
    document.addEventListener('click', handleClickOutside);

    (async () => {
      try {
        const response = await getUserSettings();
        const serverSettings = response.settings;
        readingModeScroll = serverSettings.readingModeScroll ?? true;
        darkModeOption = serverSettings.darkModeOption ?? 'dark';
        autoSaveEnabled = serverSettings.autoSaveEnabled ?? true;
        setDarkMode(darkModeOption, false);
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

  // Save a single setting to the server with a toast
  async function saveSetting(key, value) {
    // ✅ ถ้า Auto Save ถูกปิด และ key ไม่ใช่ autoSaveEnabled → ไม่ต้องบันทึกอะไรเลย
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

  // Apply theme and optionally persist to server
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

      <!-- Auto Save -->
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
            on:change={handleAutoSaveToggle}
          />
          <div class="w-11 h-6 bg-gray-300 dark:bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:bg-green-500 transition-colors duration-200"></div>
          <div class="absolute left-0.5 top-0.5 size-5 bg-white rounded-full transition-transform duration-200 peer-checked:translate-x-5"></div>
        </label>
      </div>


      <!-- Profile Management -->
      <div class="flex items-center justify-between px-6 py-5">
        <div class="flex-1">
          <h3 class="text-base font-bold text-gray-900 dark:text-gray-100">
            จัดการโปรไฟล์
          </h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">แก้ไขข้อมูลโปรไฟล์ของคุณ</p>
        </div>
        <button
          class="bg-indigo-500 hover:bg-indigo-600 text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
          on:click={() => showProfileModal = true}
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
          ไปที่โปรไฟล์
        </button>
      </div>


      <!-- Modal โปรไฟล์ -->
      {#if showProfileModal}
        <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8 w-full max-w-2xl mx-4 relative">
            
            <h2 class="text-xl font-bold mb-6 text-gray-900 dark:text-gray-100">โปรไฟล์ของฉัน</h2>
            
            <!-- Profile mock data -->
            <div class="flex items-center gap-6">
              <img src={profile.avatar} alt="avatar" class="w-20 h-20 rounded-full object-cover" />
              <div class="space-y-2">
                <div>
                  <label class="block text-sm text-gray-500">ชื่อ</label>
                  <input
                    type="text"
                    bind:value={profile.name}
                    class="w-full border rounded-lg px-3 py-2 mt-1 bg-gray-50 dark:bg-gray-700 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label class="block text-sm text-gray-500">Username</label>
                  <input
                    type="text"
                    bind:value={profile.username}
                    class="w-full border rounded-lg px-3 py-2 mt-1 bg-gray-50 dark:bg-gray-700 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label class="block text-sm text-gray-500">Email</label>
                  <input
                    type="email"
                    bind:value={profile.email}
                    class="w-full border rounded-lg px-3 py-2 mt-1 bg-gray-50 dark:bg-gray-700 dark:text-gray-100"
                  />
                </div>
              </div>
            </div>

            <!-- Action buttons -->
            <div class="mt-8 flex justify-end gap-3">
              <button 
                class="px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-lg"
                on:click={cancelProfile}
              >
                ยกเลิก
              </button>
              <button 
                class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg"
                on:click={saveProfile}
              >
                บันทึก
              </button>
            </div>
          </div>
        </div>
      {/if}

      <!-- Confirm Cancel Modal -->
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
                on:click={() => showCancelConfirm = false}
              >
                กลับไปแก้ไข
              </button>
              <button 
                class="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg"
                on:click={confirmCancel}
              >
                ไม่บันทึก
              </button>
            </div>
          </div>
        </div>
      {/if}




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
