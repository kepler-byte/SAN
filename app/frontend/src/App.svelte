<script>
  import { authToken } from "./lib/auth";
  import { onMount } from "svelte";
  import { fade, fly } from "svelte/transition";

  // Import components
  import Login from "./routes/Login.svelte";
  import Register from "./routes/Register.svelte";
  import Navbar from "./components/Navbar.svelte"; 

  // Import page components
  import Home from "./routes/Home.svelte";
  import Wallet from "./routes/Wallet.svelte";
  import Settings from "./routes/Settings.svelte";
  import Bookpreview from "./routes/Bookpreview.svelte";
  import BookTest from "./routes/BookTest.svelte";

    import { Toaster, toast } from 'svelte-sonner';

  // State
  let appState = "auth"; // "auth" หรือ "dashboard"
  let currentPage = "home"; // สำหรับ dashboard
  let previousPage = "";

  $: token = $authToken;

  // Routes
  const routes = {
    home: Home,
    wallet: Wallet,
    settings: Settings,
    booktest: BookTest,
    bookpreview: Bookpreview,
  };

  $: currentComponent = routes[currentPage] || Home;

  onMount(() => {
    if (token) {
      appState = "dashboard";

      // Init page from URL
      const initialPage = getPageFromURL();
      if (routes[initialPage]) {
        currentPage = initialPage;
      }

      history.replaceState({ page: currentPage }, "", `/${currentPage}`);
      window.addEventListener("popstate", handlePopState);

      return () => {
        window.removeEventListener("popstate", handlePopState);
      };
    } else {
      // ถ้าไม่ได้ login → เช็ค URL ว่าคือ login หรือ register
      const initialPage = getPageFromURL();
      if (initialPage === "register") {
        appState = "auth";
        page = "register";
      } else {
        appState = "auth";
        page = "login";
      }
    }
  });

  // For login/register
  let page = "login";
  function handleNavigate(target) {
    page = target;
    history.replaceState({}, "", target === "register" ? "/register" : "/");
  }

  // For dashboard
  function handleDashboardNavigation(event) {
    const newPage = event.detail;
    if (currentPage !== newPage && routes[newPage]) {
      previousPage = currentPage;
      currentPage = newPage;
      history.pushState({ page: newPage }, "", `/${newPage}`);
    }
  }

  function handlePopState(event) {
    const page = event.state?.page || getPageFromURL();
    if (page && routes[page]) {
      previousPage = currentPage;
      currentPage = page;
    }
  }

  function getPageFromURL() {
    const path = window.location.pathname.slice(1);
    if (!path) return "home";
    if (path === "login" || path === "register") return path;
    return routes[path] ? path : "home";
  }

  function getTransitionDirection() {
    const pages = Object.keys(routes);
    const currentIndex = pages.indexOf(currentPage);
    const previousIndex = pages.indexOf(previousPage);
    return currentIndex > previousIndex ? 1 : -1;
  }

  // Watch for token changes
  $: if (token && appState !== "dashboard") {
    appState = "dashboard";
    currentPage = "home";
  } else if (!token && appState === "dashboard") {
    appState = "auth";
    page = "login";
    history.replaceState({}, "", "/");
  }
</script>

<Toaster position="top-right" />

{#if !token}
  <!-- Authentication Pages -->
  <div class="min-h-screen">
    {#if page === "login"}
      <div in:fade={{ duration: 300 }} out:fade={{ duration: 300 }}>
        <Login on:navigate={e => handleNavigate(e.detail)} />
      </div>
    {:else if page === "register"}
      <div in:fade={{ duration: 300 }} out:fade={{ duration: 300 }}>
        <Register on:navigate={e => handleNavigate(e.detail)} />
      </div>
    {/if}
  </div>
{:else}
  <!-- Authenticated Dashboard -->
  <main class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Only show navbar for non-bookpreview pages -->
    {#if currentPage !== "bookpreview"}
      <Navbar {currentPage} on:navigate={handleDashboardNavigation} />
    {/if}

    <div class="{currentPage !== 'bookpreview' ? 'md:ml-20' : ''} min-h-screen">
      <div class="relative w-full min-h-screen">
        {#key currentPage}
          <div
            in:fly={{ x: 300 * getTransitionDirection(), duration: 300, delay: 150 }}
            out:fly={{ x: -300 * getTransitionDirection(), duration: 300 }}
            class="absolute inset-0 w-full"
          >
            <svelte:component this={currentComponent} on:navigate={handleDashboardNavigation} />
          </div>
        {/key}
      </div>
    </div>

    <!-- Only show bottom spacing for non-bookpreview pages -->
    {#if currentPage !== "bookpreview"}
      <div class="md:hidden h-20"></div>
    {/if}
  </main>
{/if}

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
      sans-serif;
  }

  :global(*) {
    box-sizing: border-box;
  }

  :global(html) {
    overflow-x: hidden;
  }

  .min-h-screen {
    transition: all 0.3s ease-in-out;
  }
</style>
