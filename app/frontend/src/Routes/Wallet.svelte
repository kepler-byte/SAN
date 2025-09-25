<script>
  import { House, PlusIcon, Wallet } from "@lucide/svelte";
  import { onMount } from "svelte";
  import { getCurrentUser, addPoints, processTrueMoneyPayment } from "../lib/api.js";
  import { authToken, currentUser } from "../lib/auth.js";
  import SANPoint from "../assets/SANPoint.svg";

  let userPoints = 0;
  let loading = true;
  let error = null;
  let showAddPointsModal = false;
  let showTrueMoneyModal = false;
  let pointsToAdd = 100;
  let addingPoints = false;
  let voucherHash = '';
  let processingPayment = false;

  // Load user data when component mounts
  onMount(async () => {
    try {
      if ($authToken) {
        const userData = await getCurrentUser();
        currentUser.set(userData);
        userPoints = userData.points || 0;
      }
    } catch (err) {
      error = err.message;
      console.error("Failed to load user data:", err);
    } finally {
      loading = false;
    }
  });

  // Handle adding points
  async function handleAddPoints() {
    if (!pointsToAdd || pointsToAdd <= 0) {
      error = "กรุณาใส่จำนวน Point ที่ถูกต้อง";
      return;
    }

    try {
      addingPoints = true;
      error = null;
      const result = await addPoints(pointsToAdd);
      userPoints = result.points;
      showAddPointsModal = false;
      pointsToAdd = 100; // Reset to default
      
      // Show success message
      console.log(result.message);
    } catch (err) {
      error = err.message;
      console.error("Failed to add points:", err);
    } finally {
      addingPoints = false;
    }
  }

  // Open add points modal
  function openAddPointsModal() {
    showAddPointsModal = true;
    error = null;
  }

  // Handle TrueMoney payment
  async function handleTrueMoneyPayment() {
    if (!voucherHash.trim()) {
      error = "กรุณากรอก Voucher Hash";
      return;
    }

    try {
      processingPayment = true;
      error = null;
      
      const result = await processTrueMoneyPayment(voucherHash);
      
      // Update user points
      userPoints = result.payment_details.total_points;
      
      // Close modal and reset form
      showTrueMoneyModal = false;
      voucherHash = '';
      
      // Show success message
      alert(`สำเร็จ! เติม ${result.payment_details.points_added} Point (${result.payment_details.amount_baht} บาท)`);
      
    } catch (err) {
      error = err.message;
      console.error("TrueMoney payment failed:", err);
    } finally {
      processingPayment = false;
    }
  }

  // Open TrueMoney payment modal
  function openTrueMoneyModal() {
    showTrueMoneyModal = true;
    error = null;
  }

  // Close modal
  function closeModal() {
    showAddPointsModal = false;
    pointsToAdd = 100;
    error = null;
  }

  // Format number with commas
  function formatPoints(points) {
    return points.toLocaleString();
  }
</script>

<div class="p-6 border-b border-gray-200">
  <div class="flex items-center gap-3">
    <div
      class="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center"
    >
      <Wallet class="w-4 h-4 text-gray-600" />
    </div>
    <h1 class="text-lg font-semibold text-gray-900">หน้ากระเป๋าเงิน</h1>
  </div>
</div>

<div
  class="w-full mx-auto min-h-screen bg-white flex flex-col items-center p-10"
>
  <!-- ส่วน Point -->
  <div class="w-full flex flex-col justify-start items-center gap-6 mt-12">
    <div class="flex flex-col justify-start items-center gap-2">
      <div
        class="opacity-50 text-center text-black text-lg font-normal font-['LINE_Seed_Sans_TH']"
      >
        Point ของคุณ
      </div>
      <div class="flex justify-center items-center gap-3 flex-wrap">
        {#if loading}
          <div class="text-gray-400 text-5xl font-bold font-['LINE_Seed_Sans_TH']">
            กำลังโหลด...
          </div>
        {:else if error}
          <div class="text-red-400 text-xl font-bold font-['LINE_Seed_Sans_TH']">
            เกิดข้อผิดพลาด: {error}
          </div>
        {:else}
          <div
            class="text-orange-400 text-5xl font-bold font-['LINE_Seed_Sans_TH']"
          >
            {formatPoints(userPoints)}
          </div>
          <img src={SANPoint} alt="SAN Logo" class="w-10 h-10 object-contain" />
        {/if}
      </div>
    </div>

    <!-- ปุ่ม เติม Point -->
    <div class="w-full flex flex-col gap-3">
      <!-- TrueMoney Payment Button -->
      <button
        class="w-full px-6 py-3.5 bg-green-600 hover:bg-green-700 text-white rounded-xl flex justify-center items-center gap-3 transition disabled:opacity-50 font-medium"
        on:click={openTrueMoneyModal}
        disabled={loading || error}
      >
        <svg id="Layer_2" data-name="Layer 2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 376.61 221.17" class="w-6 h-6" >
  <defs>
    <style>
      .cls-1 {
        fill: none;
      }

      .cls-2 {
        fill: #aa0017;
      }

      .cls-3 {
        fill: #ffcd00;
      }

      .cls-4 {
        fill: #ff000f;
      }

      .cls-5 {
        fill: #ff7b00;
      }
    </style>
  </defs>
  <g id="Layer_2-2" data-name="Layer 2">
    <g>
      <path class="cls-5" d="M370.14,22.23h-98.74c-6.45,0-12.19,4.08-14.31,10.17-4.7,13.51-10.01,28.73-15.48,44.43,0,0,0,0,0,0-.17.49-.34.97-.51,1.46-.12.33-.23.67-.35,1-17.07,49-35.56,102.04-42.59,122.13-.82,2.5-1.75,5.36-2.88,8.29-.2.52-1.17,3-2.96,5.44-.31.42-.61.8-.91,1.15-.52.62-1.17,1.35-2.14,2.1-.05.04-.11.08-.16.12-.33.26-.71.52-1.13.79-1.05.64-1.95.97-2.29,1.1-.05.02-.1.03-.15.05,0,0-.02,0-.02,0-.03.01-.06.02-.09.03-.02,0-.05.02-.07.02-1.27.42-2.43.6-3.38.65h118.69c.77,0,1.53-.09,2.28-.28,2.88-.74,9.06-3.42,11.65-12.95l61.66-177.12c1.46-4.2-1.66-8.59-6.11-8.59Z"/>
      <g>
        <path class="cls-1" d="M123.08,59.1h0s-.02.06-.02.06c.01-.03.02-.05.04-.08l-.02.02h0Z"/>
        <path class="cls-4" d="M77.92,187.55c.03-.07.05-.15.08-.22.08-.21.15-.43.23-.64.12-.35.24-.7.37-1.05.17-.48.33-.95.5-1.43.21-.6.42-1.19.63-1.79.25-.71.5-1.42.75-2.12.29-.81.57-1.63.86-2.44.32-.91.64-1.82.96-2.74.35-1,.7-2.01,1.06-3.01.38-1.09.76-2.18,1.15-3.26.41-1.16.82-2.33,1.23-3.49.43-1.23.87-2.47,1.3-3.7.46-1.3.91-2.59,1.37-3.89.47-1.35.95-2.71,1.42-4.06.49-1.4.98-2.8,1.48-4.21.51-1.44,1.01-2.89,1.52-4.33.52-1.48,1.04-2.95,1.56-4.43.53-1.5,1.06-3.01,1.58-4.51.53-1.52,1.07-3.05,1.6-4.57.54-1.54,1.08-3.07,1.62-4.61.54-1.54,1.08-3.09,1.62-4.63.54-1.54,1.08-3.08,1.62-4.62l1.61-4.6c.53-1.52,1.07-3.03,1.6-4.55.52-1.49,1.05-2.99,1.57-4.48.51-1.46,1.03-2.93,1.54-4.39.5-1.43,1-2.86,1.5-4.28.49-1.38.97-2.77,1.46-4.15.47-1.33.93-2.66,1.4-4,.45-1.27.89-2.55,1.34-3.82.42-1.21.85-2.42,1.27-3.62.4-1.14.8-2.27,1.2-3.41.37-1.06.74-2.11,1.11-3.17.34-.97.68-1.94,1.02-2.9.31-.87.61-1.75.92-2.62.27-.77.54-1.55.81-2.32.23-.66.47-1.33.7-1.99.19-.55.39-1.1.58-1.65.31-.89.59-1.81,1.01-2.66l.04-.04h.02s.01-.03.01-.03l.02-.02c.08-.16.11-.3.21-.46.82-1.8,2.97-3.74,3.85-4.02l-13.37-44.93c-1.67-5.72-7.16-9.65-12.87-9.65H6.64C2.2,0-.99,4.27.28,8.53l53.1,178.45c2.19,6.33,6.95,9.62,11.82,9.87,0,0,0,0,0,0,5.06.22,10.22-2.87,12.72-9.29Z"/>
        <path class="cls-2" d="M127.19,54.6s0,0,.01-.01l-.04.03s.02-.01.03-.02Z"/>
        <path class="cls-2" d="M164.03,196.09c-.22-.74-.44-1.48-.66-2.22-.11-.38-.23-.76-.34-1.14l-22.76-76.45-15.91-53.46c-.59-1.99-.39-3.99.45-5.62.2-.39.45-.76.72-1.11.03-.04.06-.09.1-.13.39-.46.84-.88,1.35-1.23.06-.04.12-.07.18-.11l.04-.03c-.88.28-3.03,2.22-3.85,4.02-.09.16-.18.32-.26.48-.01.03-.02.05-.04.08-.42.85-.7,1.77-1.01,2.66-.19.55-.39,1.1-.58,1.65-.23.66-.47,1.33-.7,1.99-.27.77-.54,1.55-.81,2.32-.31.87-.61,1.75-.92,2.62-.34.97-.68,1.94-1.02,2.9-.37,1.06-.74,2.11-1.11,3.17-.4,1.14-.8,2.27-1.2,3.41-.42,1.21-.85,2.42-1.27,3.62-.45,1.27-.89,2.55-1.34,3.82-.47,1.33-.93,2.66-1.4,4-.49,1.38-.97,2.77-1.46,4.15-.5,1.43-1,2.86-1.5,4.28-.51,1.46-1.03,2.93-1.54,4.39-.52,1.49-1.05,2.99-1.57,4.48-.53,1.52-1.07,3.03-1.6,4.55l-1.61,4.6c-.54,1.54-1.08,3.08-1.62,4.62-.54,1.54-1.08,3.09-1.62,4.63-.54,1.54-1.08,3.07-1.62,4.61-.53,1.52-1.07,3.05-1.6,4.57-.53,1.5-1.06,3.01-1.58,4.51-.52,1.48-1.04,2.95-1.56,4.43-.51,1.44-1.01,2.89-1.52,4.33-.49,1.4-.98,2.8-1.48,4.21-.47,1.35-.95,2.71-1.42,4.06-.46,1.3-.91,2.59-1.37,3.89-.43,1.23-.87,2.47-1.3,3.7-.41,1.16-.82,2.33-1.23,3.49-.38,1.09-.76,2.18-1.15,3.26-.35,1-.7,2.01-1.06,3.01-.32.91-.64,1.82-.96,2.74-.29.81-.57,1.63-.86,2.44-.25.71-.5,1.42-.75,2.12-.21.6-.42,1.19-.63,1.79-.17.48-.33.95-.5,1.43-.12.35-.24.7-.37,1.05-.08.21-.15.43-.23.64-.03.07-.05.15-.08.22-2.49,6.43-7.65,9.51-12.72,9.29,0,0,0,0,0,0-.1,0-.19.01-.28.02h99.34c-.08-.26-.15-.51-.23-.77Z"/>
        <path class="cls-3" d="M241.61,76.82c-.85-3.07-1.69-6.14-2.51-9.21-.67-2.53-1.46-4.98-2.82-7.23-1.34-2.21-3.15-4.11-5.42-5.38-.63-.35-1.29-.65-1.97-.89-1.07-.38-2.89-.65-4.03-.65h-93.51c-1.63,0-3.03.43-4.16,1.15-.01,0-.02.01-.03.02-.06.04-.12.07-.18.11-.51.35-.97.76-1.35,1.23-.03.04-.06.09-.1.13-.27.35-.52.72-.72,1.11-.84,1.63-1.04,3.63-.45,5.62l15.91,53.46,22.76,76.45,1.14,3.82,4.32,15.06c.28.8,2.57,7.02,8.88,8.98,3.1.97,5.82.49,7.21.13.21-.05.47-.12.77-.21.02,0,.05-.01.07-.02.04-.01.08-.03.12-.04.05-.02.1-.03.15-.05.35-.12,1.24-.45,2.29-1.1.43-.26.8-.53,1.13-.79.68-.53,1.19-1.03,1.56-1.41.25-.25.49-.52.74-.81.3-.35.61-.73.91-1.15,1.79-2.45,2.76-4.92,2.96-5.44,1.13-2.93,2.07-5.79,2.88-8.29.45-1.37.86-2.64,1.25-3.76.98-2.81,1.96-5.62,2.94-8.42,1.23-3.53,2.47-7.06,3.7-10.59,1.42-4.07,2.84-8.13,4.26-12.2,1.54-4.42,3.08-8.83,4.63-13.25,1.6-4.58,3.2-9.15,4.79-13.73,1.59-4.55,3.18-9.1,4.77-13.66,1.52-4.34,3.03-8.68,4.55-13.02,1.38-3.94,2.75-7.88,4.13-11.82,1.17-3.36,2.34-6.71,3.52-10.07.9-2.58,1.8-5.17,2.71-7.75.45-1.29.9-2.58,1.35-3.87.12-.33.23-.67.35-1,.17-.49.34-.97.51-1.46,0,0,0,0,0,0Z"/>
      </g>
    </g>
  </g>
</svg>
        เติมเงินด้วย TrueMoney Wallet
      </button>
      
      <!-- Manual Add Points Button -->
      <!-- <button
        class="w-full px-6 py-3.5 bg-black hover:bg-zinc-800 text-white rounded-xl flex justify-center items-center gap-3 transition disabled:opacity-50 font-['LINE_Seed_Sans_TH'] font-medium"
        on:click={openAddPointsModal}
        disabled={loading || error}
      >
        <PlusIcon class="w-4 h-4" />
        เติม Point (ทดสอบ)
      </button> -->
    </div>
  </div>

  <!-- ส่วน History -->
  <div class="w-full mt-10">
    <div
      class="w-full px-6 py-3 bg-gray-100 rounded-lg flex items-center gap-3"
    >
      <Wallet class="w-5 h-5 text-gray-600" />
      <div class="flex-1 flex flex-col justify-start items-start gap-1">
        <div
          class="text-black text-sm font-bold font-['LINE_Seed_Sans_TH'] leading-tight"
        >
          เติมเงินเข้า
        </div>
        <div
          class="text-gray-500 text-sm font-normal font-['LINE_Seed_Sans_TH'] leading-tight"
        >
          คุณได้เติมเงินเข้า 100 point
        </div>
      </div>
      <div
        class="text-gray-400 text-xs font-normal font-['LINE_Seed_Sans_TH'] leading-none"
      >
        เพิ่งส่ง
      </div>
    </div>
  </div>
</div>

<!-- Add Points Modal -->
{#if showAddPointsModal}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-2xl p-6 w-full max-w-sm">
      <h2 class="text-xl font-bold font-['LINE_Seed_Sans_TH'] text-center mb-6">
        เติม Point
      </h2>
      
      <!-- Points Input -->
      <div class="mb-6">
        <label class="block text-sm font-medium font-['LINE_Seed_Sans_TH'] text-gray-700 mb-2">
          จำนวน Point ที่ต้องการเติม
        </label>
        <input
          type="number"
          bind:value={pointsToAdd}
          min="1"
          max="10000"
          class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-orange-400 focus:border-transparent font-['LINE_Seed_Sans_TH']"
          placeholder="กรอกจำนวน Point"
        />
      </div>

      <!-- Quick select buttons -->
      <div class="grid grid-cols-3 gap-2 mb-6">
        {#each [100, 500, 1000] as quickAmount}
          <button
            class="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-['LINE_Seed_Sans_TH'] transition"
            on:click={() => pointsToAdd = quickAmount}
          >
            {quickAmount}
          </button>
        {/each}
      </div>

      <!-- Error message -->
      {#if error}
        <div class="mb-4 p-3 bg-red-100 border border-red-300 rounded-lg">
          <p class="text-red-700 text-sm font-['LINE_Seed_Sans_TH']">
            {error}
          </p>
        </div>
      {/if}

      <!-- Action buttons -->
      <div class="flex gap-3">
        <button
          class="flex-1 px-4 py-3 bg-gray-200 hover:bg-gray-300 rounded-xl font-['LINE_Seed_Sans_TH'] font-medium transition"
          on:click={closeModal}
          disabled={addingPoints}
        >
          ยกเลิก
        </button>
        <button
          class="flex-1 px-4 py-3 bg-black hover:bg-zinc-800 text-white rounded-xl font-['LINE_Seed_Sans_TH'] font-medium transition disabled:opacity-50 flex items-center justify-center gap-2"
          on:click={handleAddPoints}
          disabled={addingPoints || !pointsToAdd || pointsToAdd <= 0}
        >
          {#if addingPoints}
            <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            กำลังเติม...
          {:else}
            <PlusIcon class="w-4 h-4" />
            เติม {formatPoints(pointsToAdd)} Point
          {/if}
        </button>
      </div>
    </div>
  </div>
{/if}

<!-- TrueMoney Payment Modal -->
{#if showTrueMoneyModal}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-2xl p-6 w-full max-w-md">
      <div class="flex items-center gap-3 mb-6">
        <svg class="w-8 h-8 text-green-600" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
        <h2 class="text-xl font-bold font-['LINE_Seed_Sans_TH']">
          TrueMoney Wallet
        </h2>
      </div>
      
      <!-- Instructions -->
      <div class="mb-6 p-4 bg-blue-50 rounded-lg">
        <p class="text-sm font-['LINE_Seed_Sans_TH'] text-blue-800 mb-2">
          <strong>วิธีการเติมเงิน:</strong>
        </p>
        <ol class="text-xs font-['LINE_Seed_Sans_TH'] text-blue-700 list-decimal list-inside space-y-1">
          <li>เปิดแอป TrueMoney Wallet</li>
          <li>ส่งเงินให้เพื่อน (เบอร์ 096-668-0754)</li>
          <li>คัดลอก Link หรือ Hash ที่ได้</li>
          <li>นำมาใส่ในช่องด้านล่าง</li>
        </ol>
      </div>

      <!-- Voucher Hash Input -->
      <div class="mb-6">
        <label class="block text-sm font-medium font-['LINE_Seed_Sans_TH'] text-gray-700 mb-2">
          Voucher Hash / Link <span class="text-red-500">*</span>
        </label>
        <textarea
          bind:value={voucherHash}
          rows="3"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent font-mono text-sm resize-none"
          placeholder="ใส่ Link เต็ม หรือแค่ Hash เช่น: 01970877d4837877d3b952dc3ec4f880ccz"
        ></textarea>
        <p class="text-xs text-gray-500 font-['LINE_Seed_Sans_TH'] mt-1">
          ส่งเงินไปที่เบอร์ <strong>096-668-0754</strong> แล้วนำ Link/Hash มาใส่
        </p>
      </div>

      <!-- Error message -->
      {#if error}
        <div class="mb-4 p-3 bg-red-100 border border-red-300 rounded-lg">
          <p class="text-red-700 text-sm font-['LINE_Seed_Sans_TH']">
            {error}
          </p>
        </div>
      {/if}

      <!-- Action buttons -->
      <div class="flex gap-3">
        <button
          class="flex-1 px-4 py-3 bg-gray-200 hover:bg-gray-300 rounded-xl font-['LINE_Seed_Sans_TH'] font-medium transition"
          on:click={closeTrueMoneyModal}
          disabled={processingPayment}
        >
          ยกเลิก
        </button>
        <button
          class="flex-1 px-4 py-3 bg-green-600 hover:bg-green-700 text-white rounded-xl font-['LINE_Seed_Sans_TH'] font-medium transition disabled:opacity-50 flex items-center justify-center gap-2"
          on:click={handleTrueMoneyPayment}
          disabled={processingPayment || !voucherHash.trim()}
        >
          {#if processingPayment}
            <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            กำลังดำเนินการ...
          {:else}
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
            </svg>
            ยืนยันการชำระเงิน
          {/if}
        </button>
      </div>
    </div>
  </div>
{/if}