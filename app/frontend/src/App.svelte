<script>
  import { authToken } from "./lib/auth";
  import { onMount } from "svelte";
  import { fade, fly } from 'svelte/transition';

  // Import components
  import Login from "./Routes/Login.svelte";
  import Register from "./Routes/Register.svelte";
  import Navbar from "./components/Navbar.svelte";
  
  // Import page components
  import Home from "./Routes/Home.svelte";
  import Wallet from "./Routes/Wallet.svelte";
  import Settings from "./Routes/Settings.svelte";
  
  import toast, { Toaster } from 'svelte-french-toast';

  // State management
  let page = "login"; // ค่า default
  let currentPage = 'home'; // สำหรับ authenticated pages
  let previousPage = '';

  $: token = $authToken;

  // Page components mapping สำหรับ authenticated pages
  const routes = {
    'home': Home,
    'wallet': Wallet,
    'settings': Settings
  };

  // Get current component for authenticated pages
  $: currentComponent = routes[currentPage] || Home;

  onMount(() => {
    if (token) {
      page = "dashboard"; // เปลี่ยนเป็น dashboard แทน home
      // Set initial page from URL if authenticated
      const initialPage = getPageFromURL();
      if (routes[initialPage]) {
        currentPage = initialPage;
      }
      
      // Set initial history state
      history.replaceState({ page: currentPage }, '', `/${currentPage}`);
      
      // Listen for browser navigation
      window.addEventListener('popstate', handlePopState);
    }

    return () => {
      if (token) {
        window.removeEventListener('popstate', handlePopState);
      }
    };
  });

  // Handle navigation for login/register pages
  function handleNavigate(target) {
    page = target;
  }

  // Handle navigation for authenticated pages
  function handleDashboardNavigation(event) {
    const newPage = event.detail;
    if (currentPage !== newPage) {
      previousPage = currentPage;
      currentPage = newPage;
      
      // Update URL without page reload
      history.pushState({ page: newPage }, '', `/${newPage}`);
    }
  }

  // Handle browser back/forward buttons
  function handlePopState(event) {
    const page = event.state?.page || getPageFromURL();
    if (page && routes[page]) {
      previousPage = currentPage;
      currentPage = page;
    }
  }

  // Get page from current URL
  function getPageFromURL() {
    const path = window.location.pathname.slice(1);
    return path || 'home';
  }

  // Animation direction based on navigation
  function getTransitionDirection() {
    const pages = Object.keys(routes);
    const currentIndex = pages.indexOf(currentPage);
    const previousIndex = pages.indexOf(previousPage);
    
    return currentIndex > previousIndex ? 1 : -1;
  }

  // Watch for token changes
  $: if (token && page !== "dashboard") {
    page = "dashboard";
    currentPage = 'home';
    
  } else if (!token && page === "dashboard") {
    page = "login";
    history.replaceState({}, '', '/');
    
  }
</script>

<Toaster position="top-right" />

{#if !token}
  <!-- Authentication Pages -->
  <div class="min-h-screen">
    {#if page === "login"}
      <div in:fade="{{ duration: 300 }}" out:fade="{{ duration: 300 }}">
        <Login on:navigate={e => handleNavigate(e.detail)} />
      </div>
    {:else if page === "register"}
      <div in:fade="{{ duration: 300 }}" out:fade="{{ duration: 300 }}">
        <Register on:navigate={e => handleNavigate(e.detail)} />
      </div>
    {/if}
  </div>
{:else}
  <!-- Authenticated Dashboard -->
  <main class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Navbar -->
    <Navbar 
      {currentPage} 
      on:navigate={handleDashboardNavigation} 
    />

    <!-- Main Content Area -->
    <div class="md:ml-20 min-h-screen">
      <!-- Page Content with Animation -->
      <div class="relative w-full min-h-screen">
        {#key currentPage}
          <div 
            in:fly="{{ x: 300 * getTransitionDirection(), duration: 300, delay: 150 }}"
            out:fly="{{ x: -300 * getTransitionDirection(), duration: 300 }}"
            class="absolute inset-0 w-full"
          >
            <svelte:component this={currentComponent} />
          </div>
        {/key}
      </div>
    </div>

    <!-- Mobile bottom padding -->
    <div class="md:hidden h-20"></div>
  </main>
{/if}

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }

  :global(*) {
    box-sizing: border-box;
  }

  /* Prevent horizontal scrolling during transitions */
  :global(html) {
    overflow-x: hidden;
  }

  /* Smooth transitions */
  .min-h-screen {
    transition: all 0.3s ease-in-out;
  }
</style>