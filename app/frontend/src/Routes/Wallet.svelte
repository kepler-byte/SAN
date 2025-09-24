<script>
  import { House, PlusIcon, Wallet } from "@lucide/svelte";
  import SANPoint from "../assets/SANPoint.svg";
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
        <div
          class="text-orange-400 text-5xl font-bold font-['LINE_Seed_Sans_TH']"
        >
          2,000
        </div>
        <img src={SANPoint} alt="SAN Logo" class="w-10 h-10 object-contain" />
      </div>
    </div>

    <!-- ปุ่ม เติม Point -->
    <div class="w-full flex justify-center">
      <button
        class="flex-1 px-6 py-3.5 bg-black rounded-xl flex justify-center items-center gap-3 hover:bg-zinc-800 transition"
      >
        <PlusIcon class="w-4 h-4 text-white" />

        <span class="text-white text-sm font-bold font-['LINE_Seed_Sans_TH']"
          >เติม Point</span
        >
      </button>
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
          คุณได้เติมเงินเข้า 40 point
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
