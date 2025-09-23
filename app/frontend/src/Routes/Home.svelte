<script>
  import { clearAuth } from "../lib/auth";

  function logout() {
    clearAuth();
    location.reload();
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
</div>