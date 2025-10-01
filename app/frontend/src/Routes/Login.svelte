<script>
  import { createEventDispatcher } from "svelte";
  import { login } from "../lib/api";
  import { setAuthToken } from "../lib/auth";
  import SAN_logo from "../assets/SAN_logo.svg";
  import { Toaster, toast } from 'svelte-sonner'

  let username = "";
  let password = "";
  let error = "";
  let isLoading = false; // เพิ่ม loading state

  const dispatch = createEventDispatcher();

  async function handleLogin(e) {
    e.preventDefault();
    
    // ป้องกันการส่งซ้ำ
    if (isLoading) {
      return;
    }
    
    // ตรวจสอบข้อมูลก่อนส่ง
    if (!username.trim()) {
      error = "กรุณากรอก Username";
      toast.error("กรุณากรอก Username");
      return;
    }
    
    if (!password.trim()) {
      error = "กรุณากรอกรหัสผ่าน";
      toast.error("กรุณากรอกรหัสผ่าน");
      return;
    }
    
    // ล้าง error ก่อนทำการส่งข้อมูล
    error = "";
    isLoading = true; // เปิด loading state
    
    try {
      const res = await login({ username, password });
      setAuthToken(res.access_token);
      toast.success("เข้าสู่ระบบสำเร็จ 🎉");
      dispatch("navigate", "dashboard"); // ส่ง event ไป App.svelte
    } catch (err) {
      toast.error("เข้าสู่ระบบไม่สำเร็จ");
      error = err.message;
    } finally {
      isLoading = false; // ปิด loading state
    }
  }
</script>


<div class="min-h-screen flex items-center justify-center bg-white px-4">
  <div class="relative z-10 w-full max-w-4xl bg-white rounded-2xl flex flex-col md:flex-row shadow-lg overflow-hidden">
    
    <!-- Left Image -->
    <div
      class="hidden md:flex flex-col justify-center p-8 bg-cover bg-center w-1/2 text-white"
      style="background-image: url('https://images.unsplash.com/photo-1510172951991-856a654063f9?q=80&w=987&auto=format&fit=crop');"
    ></div>

    <!-- Right Form -->
    <div class="w-full md:w-1/2 p-10 flex flex-col items-center gap-10">
      <!-- Logo -->
      <div class="w-20 h-20 relative">
        <img src={SAN_logo} alt="SAN Logo" class="w-full h-full object-contain" />
      </div>

      <!-- Title -->
      <h1 class="text-3xl md:text-4xl font-bold text-zinc-950 text-center">
        ล็อคอิน
      </h1>

      {#if error}
        <p class="text-red-500 text-sm">{error}</p>
      {/if}

      <!-- Form -->
      <form on:submit|preventDefault={handleLogin} class="w-full flex flex-col gap-6">
        <!-- Username -->
        <div class="flex flex-col gap-2">
          <label class="text-xs font-bold text-black">Username</label>
          <input
            type="text"
            bind:value={username}
            placeholder="MangoLover99"
            required
            class="w-full h-14 px-4 bg-gray-50 rounded-xl text-base text-neutral-700 focus:outline-none focus:ring-2 focus:ring-orange-400"
          />
        </div>

        <!-- Password -->
        <div class="flex flex-col gap-2">
          <label class="text-xs font-bold text-black">Password</label>
          <input
            type="password"
            bind:value={password}
            placeholder="**********"
            required
            class="w-full h-14 px-4 bg-gray-50 rounded-xl text-base text-neutral-700 focus:outline-none focus:ring-2 focus:ring-orange-400"
          />
        </div>

        <!-- Submit -->
        <button
          type="submit"
          class="w-full h-14 bg-orange-500 rounded-2xl shadow-md text-white font-bold text-base hover:bg-orange-600 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
          disabled={!username.trim() || !password.trim() || isLoading}
        >
          {#if isLoading}
            <div class="flex items-center justify-center gap-2">
              <div class="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
              กำลังเข้าสู่ระบบ...
            </div>
          {:else}
            เข้าสู่ระบบ
          {/if}
        </button>

        <!-- Link to Register -->
        <div class="flex justify-center gap-2 text-base">
          <span class="text-gray-500">ยังไม่มีบัญชี?</span>
          <a href="#" class="text-orange-500 hover:underline" on:click={() => dispatch("navigate", "register")}>
            สมัครสมาชิก
          </a>
        </div>
      </form>
    </div>
  </div>
</div>