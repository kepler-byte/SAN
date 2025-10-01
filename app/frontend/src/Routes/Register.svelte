<script>
  import { createEventDispatcher } from "svelte";
  import { Toaster, toast } from 'svelte-sonner'
    import SAN_logo from "../assets/SAN_logo.svg";
  import { register } from "../lib/api";

  let username = "";
  let email = "";
  let password = "";
  let error = "";
  let success = "";

  const dispatch = createEventDispatcher();

  async function handleRegister(e) {
    e.preventDefault();
    
    // ตรวจสอบข้อมูลก่อนส่ง
    if (!username.trim()) {
      error = "กรุณากรอก Username";
      toast.error("กรุณากรอก Username");
      return;
    }
    
    if (!email.trim()) {
      error = "กรุณากรอก Email";
      toast.error("กรุณากรอก Email");
      return;
    }
    
    if (!password.trim()) {
      error = "กรุณากรอกรหัสผ่าน";
      toast.error("กรุณากรอกรหัสผ่าน");
      return;
    }
    
    // ตรวจสอบรูปแบบ email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      error = "รูปแบบ Email ไม่ถูกต้อง";
      toast.error("รูปแบบ Email ไม่ถูกต้อง");
      return;
    }
    
    // ตรวจสอบความยาวรหัสผ่าน
    if (password.length < 6) {
      error = "รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร";
      toast.error("รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร");
      return;
    }
    
    // ล้าง error ก่อนทำการส่งข้อมูล
    error = "";
    
    try {
      await register({ username, email, password });
      success = "";
      toast.success("สมัครสมาชิกสำเร็จ! กำลังพาไปหน้าเข้าสู่ระบบ...");
      error = "";
      setTimeout(() => dispatch("navigate", "login"), 1500);
    } catch (err) {
        toast.error("สมัครสมาชิกไม่สำเร็จ");
      error = err.message;
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
        สมัครสมาชิก
      </h1>

      {#if error}
        <p class="text-red-500 text-sm">{error}</p>
      {/if}
      {#if success}
        <p class="text-green-500 text-sm">{success}</p>
      {/if}

      <!-- Form -->
      <form on:submit|preventDefault={handleRegister} class="w-full flex flex-col gap-6">
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

        <!-- Email -->
        <div class="flex flex-col gap-2">
          <label class="text-xs font-bold text-black">Email</label>
          <input
            type="email"
            bind:value={email}
            placeholder="🥭 example@mango.tree"
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
            minlength="6"
            class="w-full h-14 px-4 bg-gray-50 rounded-xl text-base text-neutral-700 focus:outline-none focus:ring-2 focus:ring-orange-400"
          />
        </div>

        <!-- Submit -->
        <button
          type="submit"
          class="w-full h-14 bg-orange-500 rounded-2xl shadow-md text-white font-bold text-base hover:bg-orange-600 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
          disabled={!username.trim() || !email.trim() || !password.trim()}
        >
          สมัครสมาชิก
        </button>

        <!-- Link to Login -->
        <div class="flex justify-center gap-2 text-base">
          <span class="text-gray-500">มีบัญชีอยู่แล้ว?</span>
          <a href="#" class="text-orange-500 hover:underline" on:click={() => dispatch("navigate", "login")}>
            เข้าสู่ระบบ
          </a>
        </div>
      </form>
    </div>
  </div>
</div>