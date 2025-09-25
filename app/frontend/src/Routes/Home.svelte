<script>
  import { clearAuth } from "../lib/auth";
  import { House } from "@lucide/svelte";
  function logout() {
    clearAuth();
    location.reload();
  }
</script>

<div class="p-6 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
    <div class="flex items-center gap-3">
        <div class="w-8 h-8 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
            <House class="w-4 h-4 text-gray-600 dark:text-gray-300" />
        </div>
        <h1 class="text-lg font-semibold text-gray-900 dark:text-gray-100">หน้าหลัก</h1>
    </div>
</div>


<div class="flex flex-col items-center justify-center h-screen bg-gray-50">
  <h1 class="text-3xl font-bold mb-4">Welcome to Home 🎉</h1>
  <button
    on:click={logout}
    class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded"
  >
    Logout
  </button>
</div>