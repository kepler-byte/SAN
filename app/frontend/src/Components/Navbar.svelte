<script>
  import { onMount, createEventDispatcher } from 'svelte';
  export let currentPage = 'home'; // รับค่าจาก parent component
  
  let isMobile = false;
  let hoveredItem = null;
  
  const dispatch = createEventDispatcher();

  const items = [
    { icon: 'home', label: 'หน้าหลัก', page: 'home' },
    { icon: 'book', label: 'คลังหนังสือ', page: 'bookstore' },
    { icon: 'account_balance_wallet', label: 'เติมเงิน', page: 'wallet' },
    { icon: 'settings', label: 'การตั้งค่า', page: 'settings' }
  ];

  function checkScreenSize() {
    if (window.innerWidth < 768) {
      isMobile = true;
    } else {
      isMobile = false;
    }
  }

  function handleMouseEnter(item) {
    if (!isMobile) {
      hoveredItem = item;
    }
  }

  function handleMouseLeave() {
    if (!isMobile) {
      hoveredItem = null;
    }
  }

  function navigateTo(page) {
    if (currentPage !== page) {
      dispatch('navigate', page);
    }
  }

  onMount(() => {
    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
    return () => window.removeEventListener('resize', checkScreenSize);
  });
</script>

{#if isMobile}
  <!-- Mobile Navbar -->
  <nav class="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 flex justify-around items-center py-3 z-10 md:hidden">
    {#each items as item (item.label)}
      <button
        class="flex flex-col items-center justify-center transition-colors duration-200"
        aria-label={item.label}
        on:click={() => navigateTo(item.page)}
      >
        <span class="material-symbols-outlined text-xl transition-colors duration-200 {currentPage === item.page ? 'text-orange-500' : 'text-gray-500 dark:text-gray-400'}">
          {item.icon}
        </span>
        <span class="text-xs mt-1 transition-colors duration-200 {currentPage === item.page ? 'text-orange-500 font-medium' : 'text-gray-500 dark:text-gray-400'}">
          {item.label}
        </span>
      </button>
    {/each}
  </nav>
{:else}
  <!-- Desktop Sidebar -->
  <aside class="hidden md:flex md:flex-col md:w-20 hover:md:w-48 md:h-screen md:bg-white dark:md:bg-gray-800 md:border-r md:border-gray-200 dark:md:border-gray-700 md:fixed md:top-0 md:left-0 md:bottom-0 md:transition-all md:duration-300 md:ease-in-out md:z-10">
    <div class="flex flex-col py-6 space-y-2 w-full">
      {#each items as item (item.label)}
        <button
          class="flex items-center w-full hover:bg-gray-50 dark:hover:bg-gray-700 transition-all duration-200 group relative {currentPage === item.page ? 'bg-orange-50 dark:bg-orange-900/20 border-r-2 border-orange-500' : ''}"
          aria-label={item.label}
          on:mouseenter={() => handleMouseEnter(item)}
          on:mouseleave={handleMouseLeave}
          on:click={() => navigateTo(item.page)}
        >
          <!-- Icon Container -->
          <div class="w-20 flex justify-center py-3">
            <span class="material-symbols-outlined text-2xl transition-colors duration-200 {currentPage === item.page ? 'text-orange-500' : 'text-gray-500 dark:text-gray-400'} group-hover:text-orange-500">
              {item.icon}
            </span>
          </div>
          <!-- Text on hover -->
          <span class="absolute left-20 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap pointer-events-none {currentPage === item.page ? 'text-orange-500' : 'text-gray-500 dark:text-gray-400'} group-hover:text-orange-500">
            {item.label}
          </span>
        </button>
      {/each}
    </div>
  </aside>
{/if}

<style>
  .material-symbols-outlined {
    font-variation-settings:
      'FILL' 0,
      'wght' 400,
      'GRAD' 0,
      'opsz' 24
  }

  /* Hover shadow for sidebar */
  aside:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  /* Mobile active indicator */
  @media (max-width: 767px) {
    button::before {
      content: '';
      position: absolute;
      top: -1px;
      left: 50%;
      transform: translateX(-50%);
      width: 0;
      height: 3px;
      background-color: #f97316;
      border-radius: 0 0 2px 2px;
      transition: width 0.3s ease;
    }
    
    button.active::before {
      width: 24px;
    }
  }
</style>