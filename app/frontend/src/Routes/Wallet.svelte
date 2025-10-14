<script>
  import { House, PlusIcon, Wallet } from "@lucide/svelte";
  import { onMount } from "svelte";
  import { getCurrentUser, addPoints, processTrueMoneyPayment, getPaymentHistory } from "../lib/api.js";
  import { authToken, currentUser } from "../lib/auth.js";
  import { Toaster, toast } from 'svelte-sonner';
  import SANPoint from "../assets/SANPoint.svg";

  let userPoints = 0;
  let loading = true;
  let error = null;
  let showAddPointsModal = false;
  let showTrueMoneyModal = false;
  let showHistoryModal = false;
  let pointsToAdd = 100;
  let addingPoints = false;
  let voucherHash = '';
  let processingPayment = false;
  let paymentHistory = [];
  let loadingHistory = false;

  // Load user data when component mounts
  onMount(async () => {
    try {
      if ($authToken) {
        const userData = await getCurrentUser();
        currentUser.set(userData);
        userPoints = userData.points || 0;
        
        // Load recent payment history for preview
        const historyResult = await getPaymentHistory(1, 0);
        paymentHistory = historyResult.history;
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

  function formatThaiDate(dateString) {
    if (!dateString) return "";

    const date = new Date(dateString);
    return date.toLocaleDateString("th-TH", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  }

  function openHistoryModal() {
    showHistoryModal = true;
    error = null;

    // โหลดประวัติทั้งหมด (20 รายการ)
    loadHistory();
  }

  function closeHistoryModal() {
    showHistoryModal = false;
  }

  async function loadHistory() {
    try {
      loadingHistory = true;
      const historyResult = await getPaymentHistory(20, 0);
      paymentHistory = historyResult.history;
    } catch (err) {
      error = err.message;
      console.error("Failed to load history:", err);
    } finally {
      loadingHistory = false;
    }
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
      toast.success(`สำเร็จ! เติม ${result.payment_details.points_added} Point (${result.payment_details.amount_baht} บาท)`);
      
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

// Close TrueMoney payment modal
  function closeTrueMoneyModal() {
    showTrueMoneyModal = false;
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
<!-- Header -->
<div class="p-6 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
    <div class="flex items-center gap-3">
        <div class="w-8 h-8 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
            <Wallet class="w-4 h-4 text-gray-600 dark:text-gray-300" />
        </div>
        <h1 class="text-lg font-semibold text-gray-900 dark:text-gray-100">เติมเงิน</h1>
    </div>
</div>

<!-- Main Content -->
<div
  class="w-full mx-auto min-h-screen bg-white dark:bg-gray-900 flex flex-col items-center p-10"
>
  <!-- ส่วน Point -->
  <div class="w-full flex flex-col justify-start items-center gap-6 mt-12">
    <div class="flex flex-col justify-start items-center gap-2">
      <div
        class="opacity-50 text-center text-black dark:text-gray-300 text-lg font-normal font-['LINE_Seed_Sans_TH']"
      >
        Point ของคุณ
      </div>
      <div class="flex justify-center items-center gap-3 flex-wrap">
        {#if loading}
          <div class="text-gray-400 dark:text-gray-500 text-5xl font-bold font-['LINE_Seed_Sans_TH']">
            กำลังโหลด...
          </div>
        {:else if error}
          <div class="text-red-400 dark:text-red-300 text-xl font-bold font-['LINE_Seed_Sans_TH']">
            เกิดข้อผิดพลาด: {error}
          </div>
        {:else}
          <div
            class="text-orange-400 dark:text-orange-300 text-5xl font-bold font-['LINE_Seed_Sans_TH']"
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
        class="w-full px-6 py-3.5 bg-green-600 hover:bg-green-700 text-white rounded-xl flex justify-center items-center gap-3 transition disabled:opacity-50 font-['LINE_Seed_Sans_TH'] font-medium"
        on:click={openTrueMoneyModal}
        disabled={loading || error}
      >
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
        เติมเงินด้วย TrueMoney Wallet
      </button>
      
      <!-- Manual Add Points Button -->
      <button
        class="w-full px-6 py-3.5 bg-black dark:bg-gray-800 hover:bg-zinc-800 dark:hover:bg-gray-700 text-white rounded-xl flex justify-center items-center gap-3 transition disabled:opacity-50 font-['LINE_Seed_Sans_TH'] font-medium"
        on:click={openAddPointsModal}
        disabled={loading || error}
      >
        <PlusIcon class="w-4 h-4" />
        เติม Point (ทดสอบ)
      </button>
    </div>
  </div>

  <!-- ส่วน History -->
  <div class="w-full mt-10">
    <div class="flex justify-between items-center mb-4">
      <h3 class="text-lg font-bold font-['LINE_Seed_Sans_TH'] text-gray-900 dark:text-gray-100">
        ประวัติการทำรายการ
      </h3>
      <button
        class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm font-medium font-['LINE_Seed_Sans_TH'] transition"
        on:click={openHistoryModal}
      >
        ดูทั้งหมด →
      </button>
    </div>

    {#if paymentHistory.length > 0}
      <div class="w-full px-6 py-3 bg-gray-100 dark:bg-gray-800 rounded-lg flex items-center gap-3">
        <Wallet class="w-5 h-5 text-gray-600 dark:text-gray-400" />
        <div class="flex-1 flex flex-col justify-start items-start gap-1">
          <div class="text-black dark:text-white text-sm font-bold font-['LINE_Seed_Sans_TH'] leading-tight">
            เติมเงินด้วย TrueMoney
          </div>
          <div class="text-gray-500 dark:text-gray-400 text-sm font-normal font-['LINE_Seed_Sans_TH'] leading-tight">
            +{formatPoints(paymentHistory[0].points_added)} Point ({paymentHistory[0].amount_baht} บาท)
          </div>
        </div>
        <div class="text-gray-400 dark:text-gray-500 text-xs font-normal font-['LINE_Seed_Sans_TH'] leading-none">
          {formatThaiDate(paymentHistory[0].created_at)}
        </div>
      </div>
    {:else}
      <div class="w-full px-6 py-8 bg-gray-50 dark:bg-gray-800 rounded-lg flex flex-col items-center gap-3">
        <Wallet class="w-8 h-8 text-gray-400 dark:text-gray-500" />
        <p class="text-gray-500 dark:text-gray-400 text-sm font-['LINE_Seed_Sans_TH'] text-center">
          ยังไม่มีประวัติการทำรายการ<br>
          เริ่มเติมเงินเพื่อดูประวัติได้เลย!
        </p>
      </div>
    {/if}
  </div>
</div>

<!-- Add Points Modal -->
{#if showAddPointsModal}
  <div class="fixed inset-0 bg-black bg-opacity-50 dark:bg-black dark:bg-opacity-70 flex items-center justify-center z-50 p-4">
    <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 w-full max-w-sm">
      <h2 class="text-xl font-bold font-['LINE_Seed_Sans_TH'] text-center mb-6 text-gray-900 dark:text-gray-100">
        เติม Point
      </h2>
      
      <div class="mb-6">
        <label class="block text-sm font-medium font-['LINE_Seed_Sans_TH'] text-gray-700 dark:text-gray-300 mb-2">
          จำนวน Point ที่ต้องการเติม
        </label>
        <input
          type="number"
          bind:value={pointsToAdd}
          min="1"
          max="10000"
          class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-orange-400 focus:border-transparent font-['LINE_Seed_Sans_TH'] bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          placeholder="กรอกจำนวน Point"
        />
      </div>

      <div class="grid grid-cols-3 gap-2 mb-6">
        {#each [100, 500, 1000] as quickAmount}
          <button
            class="px-3 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg text-sm font-['LINE_Seed_Sans_TH'] text-gray-900 dark:text-gray-200 transition"
            on:click={() => pointsToAdd = quickAmount}
          >
            {quickAmount}
          </button>
        {/each}
      </div>

      {#if error}
        <div class="mb-4 p-3 bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-700 rounded-lg">
          <p class="text-red-700 dark:text-red-300 text-sm font-['LINE_Seed_Sans_TH']">
            {error}
          </p>
        </div>
      {/if}

      <div class="flex gap-3">
        <button
          class="flex-1 px-4 py-3 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-xl font-['LINE_Seed_Sans_TH'] font-medium text-gray-900 dark:text-gray-200 transition"
          on:click={closeModal}
          disabled={addingPoints}
        >
          ยกเลิก
        </button>
        <button
          class="flex-1 px-4 py-3 bg-black dark:bg-gray-800 hover:bg-zinc-800 dark:hover:bg-gray-700 text-white rounded-xl font-['LINE_Seed_Sans_TH'] font-medium transition disabled:opacity-50 flex items-center justify-center gap-2"
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

<!-- Payment History Modal -->
{#if showHistoryModal}
  <div class="fixed inset-0 bg-black bg-opacity-50 dark:bg-black dark:bg-opacity-70 flex items-center justify-center z-50 p-4">
    <div class="bg-white dark:bg-gray-800 rounded-2xl w-full max-w-2xl max-h-[80vh] flex flex-col">
      <div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-bold font-['LINE_Seed_Sans_TH'] text-gray-900 dark:text-gray-100">
          ประวัติการทำรายการ
        </h2>
        <button
          class="w-8 h-8 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-full flex items-center justify-center transition"
          on:click={closeHistoryModal}
        >
          <svg class="w-4 h-4 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <div class="flex-1 overflow-y-auto p-6">
        {#if loadingHistory}
          <div class="flex items-center justify-center py-12">
            <div class="w-8 h-8 border-4 border-gray-300 dark:border-gray-600 border-t-blue-500 rounded-full animate-spin"></div>
          </div>
        {:else if paymentHistory.length === 0}
          <div class="flex flex-col items-center justify-center py-12 text-center">
            <Wallet class="w-16 h-16 text-gray-300 dark:text-gray-600 mb-4" />
            <h3 class="text-lg font-semibold font-['LINE_Seed_Sans_TH'] text-gray-600 dark:text-gray-400 mb-2">
              ยังไม่มีประวัติการทำรายการ
            </h3>
            <p class="text-gray-500 dark:text-gray-400 font-['LINE_Seed_Sans_TH']">
              เริ่มเติมเงินเพื่อดูประวัติการทำรายการได้เลย!
            </p>
          </div>
        {:else}
          <div class="space-y-4">
            {#each paymentHistory as payment, index (payment.id || index)}
              <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition">
                <div class="flex items-start justify-between">
                  <div class="flex items-start gap-3">
                    <div class="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center mt-1">
                      <svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                      </svg>
                    </div>
                    
                    <div class="flex-1">
                      <h4 class="font-semibold font-['LINE_Seed_Sans_TH'] text-gray-900 dark:text-gray-100">
                        เติมเงินด้วย TrueMoney Wallet
                      </h4>
                      <p class="text-sm text-gray-600 dark:text-gray-400 font-['LINE_Seed_Sans_TH'] mt-1">
                        +{formatPoints(payment.points_added)} Point ({payment.amount_baht} บาท)
                      </p>
                      <p class="text-xs text-gray-500 dark:text-gray-500 font-['LINE_Seed_Sans_TH'] mt-2">
                        Voucher ID: {payment.id.substring(0, 16)}...
                      </p>
                    </div>
                  </div>

                  <div class="text-right">
                    <div class="inline-flex items-center px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 rounded-full text-xs font-medium font-['LINE_Seed_Sans_TH'] mb-2">
                      สำเร็จ
                    </div>
                    <p class="text-xs text-gray-500 dark:text-gray-500 font-['LINE_Seed_Sans_TH']">
                      {formatThaiDate(payment.created_at)}
                    </p>
                  </div>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>

      <div class="p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 rounded-b-2xl">
        <div class="flex items-center justify-between text-sm font-['LINE_Seed_Sans_TH'] text-gray-600 dark:text-gray-400">
          <span>
            ทั้งหมด {paymentHistory.length} รายการ
          </span>
          <span>
            แสดงรายการล่าสุด 20 รายการ
          </span>
        </div>
      </div>
    </div>
  </div>
{/if}

<!-- TrueMoney Payment Modal -->
{#if showTrueMoneyModal}
  <div class="fixed inset-0 bg-black bg-opacity-50 dark:bg-black dark:bg-opacity-70 flex items-center justify-center z-50 p-4">
    <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 w-full max-w-md">
      <div class="flex items-center gap-3 mb-6">
        <svg class="w-8 h-8 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
        <h2 class="text-xl font-bold font-['LINE_Seed_Sans_TH'] text-gray-900 dark:text-gray-100">
          TrueMoney Wallet
        </h2>
      </div>
      
      <div class="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
        <p class="text-sm font-['LINE_Seed_Sans_TH'] text-blue-800 dark:text-blue-300 mb-2">
          <strong>วิธีการเติมเงิน:</strong>
        </p>
        <ol class="text-xs font-['LINE_Seed_Sans_TH'] text-blue-700 dark:text-blue-300 list-decimal list-inside space-y-1">
          <li>เปิดแอป TrueMoney Wallet</li>
          <li>คัดลอก Link หรือ Hash ที่ได้</li>
          <li>นำมาใส่ในช่องด้านล่าง</li>
        </ol>
      </div>

      <div class="mb-6">
        <label class="block text-sm font-medium font-['LINE_Seed_Sans_TH'] text-gray-700 dark:text-gray-300 mb-2">
          Voucher Hash / Link <span class="text-red-500">*</span>
        </label>
        <textarea
          bind:value={voucherHash}
          rows="3"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent font-mono text-sm resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          placeholder="ใส่ Link เต็ม หรือแค่ Hash เช่น: 01970877d4837877d3b952dc3ec4f880ccz"
        ></textarea>
        <p class="text-xs text-gray-500 dark:text-gray-400 font-['LINE_Seed_Sans_TH'] mt-1">
          ส่งเงินไปที่เบอร์ <strong class="text-gray-900 dark:text-white">096-668-0754</strong> แล้วนำ Link/Hash มาใส่
        </p>
      </div>

      {#if error}
        <div class="mb-4 p-3 bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-700 rounded-lg">
          <p class="text-red-700 dark:text-red-300 text-sm font-['LINE_Seed_Sans_TH']">
            {error}
          </p>
        </div>
      {/if}

      <div class="flex gap-3">
        <button
          class="flex-1 px-4 py-3 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-xl font-['LINE_Seed_Sans_TH'] font-medium text-gray-900 dark:text-gray-200 transition"
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