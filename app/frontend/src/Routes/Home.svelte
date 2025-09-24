<script>
  import { clearAuth } from "../lib/auth";
  import Navbar from "../Components/Navbar.svelte";
  function logout() {
    clearAuth();
    location.reload();
  }

  let currentPage = 'home';
  
  function handleNavigation(event) {
    currentPage = event.detail;
    // เพิ่มโค้ดสำหรับเปลี่ยนหน้าตรงนี้
    console.log('Navigate to:', currentPage);
  }
</script>

<div class="flex flex-col items-center justify-center h-screen bg-gray-50">
  <h1 class="text-3xl font-bold mb-4">Welcome to Home 🎉</h1>
  <button
    on:click={logout}
    class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded"
  >
    Logout
  </button>
    <Navbar 
  {currentPage} 
  on:navigate={handleNavigation} 
/>
</div>