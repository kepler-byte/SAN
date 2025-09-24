<script>
  import { onMount } from 'svelte';

  let isMobile = false;
  let hoveredItem = null;

  const items = [
    { icon: 'home', label: 'Home', active: true },
    { icon: 'book', label: 'Document', active: false },
    { icon: 'account_balance_wallet', label: 'Wallet', active: true },
    { icon: 'settings', label: 'Settings', active: false }
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

  onMount(() => {
    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
    return () => window.removeEventListener('resize', checkScreenSize);
  });
</script>

{#if isMobile}
  <!-- Mobile Navbar -->
  <nav class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 flex justify-around items-center py-3 z-10 md:hidden">
    {#each items as item (item.label)}
      <button
        class="flex flex-col items-center justify-center"
        aria-label={item.label}
      >
        <span class="material-symbols-outlined text-xl {item.active ? 'text-black' : 'text-gray-500'}">
          {item.icon}
        </span>
        <span class="text-xs mt-1">{item.label}</span>
      </button>
    {/each}
  </nav>
{:else}
  <!-- Desktop Sidebar -->
  <aside class="hidden md:flex md:flex-col md:w-20 hover:md:w-48 md:h-screen md:bg-white md:border-r md:border-gray-200 md:fixed md:top-0 md:left-0 md:bottom-0 md:transition-all md:duration-300 md:ease-in-out md:z-10">
    <div class="flex flex-col py-6 space-y-8 w-full">
      {#each items as item (item.label)}
        <button
          class="flex items-center w-full hover:bg-gray-50 transition-colors duration-200 group relative"
          aria-label={item.label}
          on:mouseenter={() => handleMouseEnter(item)}
          on:mouseleave={handleMouseLeave}
        >
          <!-- Icon Container - ตรงกลางเมื่อไม่ hover -->
          <div class="w-20 flex justify-center py-2 ">
            <span class="material-symbols-outlined text-2xl {item.active ? 'text-black' : 'text-gray-500'} group-hover:text-black transition-colors duration-200">
              {item.icon}
            </span>
          </div>
          <!-- Text - แสดงเมื่อ hover -->
          <span class="absolute left-20 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap {item.active ? 'text-black' : 'text-gray-500'} group-hover:text-black pointer-events-none">
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

  /* เพิ่ม custom hover effect */
  aside:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
</style>