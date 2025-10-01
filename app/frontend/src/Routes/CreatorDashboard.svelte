<script>
  import { BookOpenCheck, ChevronUp, CircleDollarSign, Download, MessageCircle, Plane, Plus } from "@lucide/svelte";
  import { Chart, LineController, LineElement, PointElement, LinearScale, CategoryScale, Title, Tooltip, Legend } from 'chart.js';
  import { onMount } from "svelte";

  // Register chart.js components
  Chart.register(LineController, LineElement, PointElement, LinearScale, CategoryScale, Title, Tooltip, Legend);

  let creator = {
    name: "มะม่วงเปรี้ยวกรอบ",
    username: "@username",
    avatar: "/avatar.png",
  };

  let activeChart = 0;
  const charts = [0, 1, 2, 3];

  let stats = [
    { label: "Total Follower", value: 40689 },
    { label: "Total Reader", value: 40689 },
    { label: "Total Like", value: 40689 },
    { label: "Total Sales", value: 40689 },
  ];

  // multiple datasets for pagination
  const datasets = [
    [
      { month: "May", value: 600 },
      { month: "Jun", value: 550 },
      { month: "Jul", value: 420 },
      { month: "Aug", value: 800 },
      { month: "Sep", value: 620 },
      { month: "Oct", value: 480 },
    ],
    [
      { month: "May", value: 300 },
      { month: "Jun", value: 700 },
      { month: "Jul", value: 500 },
      { month: "Aug", value: 900 },
      { month: "Sep", value: 750 },
      { month: "Oct", value: 650 },
    ],
    [
      { month: "May", value: 800 },
      { month: "Jun", value: 400 },
      { month: "Jul", value: 600 },
      { month: "Aug", value: 720 },
      { month: "Sep", value: 580 },
      { month: "Oct", value: 500 },
    ],
    [
      { month: "May", value: 450 },
      { month: "Jun", value: 500 },
      { month: "Jul", value: 470 },
      { month: "Aug", value: 490 },
      { month: "Sep", value: 510 },
      { month: "Oct", value: 530 },
    ],
  ];

  let books = [
    { title: "Yves Saint Laurent", price: 10, pages: 10, comments: 10 },
    { title: "Book 2", price: 10, pages: 10, comments: 10 },
    { title: "Book 3", price: 10, pages: 10, comments: 10 },
  ];

  let chartCanvas;
  let chart;

  function renderChart(index) {
    const sales = datasets[index];
    if (!chart) {
      chart = new Chart(chartCanvas, {
        type: 'line',
        data: {
          labels: sales.map(s => s.month),
          datasets: [{
            label: 'Sales',
            data: sales.map(s => s.value),
            borderColor: '#f97316',
            backgroundColor: 'rgba(249, 115, 22, 0.2)',
            borderWidth: 2,
            pointRadius: 4,
            pointBackgroundColor: '#f97316',
            tension: 0.3,
            fill: true,
          }]
        },
        options: {
          responsive: true,
          animation: { duration: 600 }, // smooth transition
          plugins: {
            legend: { display: false },
            tooltip: { mode: 'index', intersect: false }
          },
          scales: {
            x: { grid: { display: false } },
            y: { beginAtZero: true }
          }
        }
      });
    } else {
      // update chart dynamically
      chart.data.labels = sales.map(s => s.month);
      chart.data.datasets[0].data = sales.map(s => s.value);
      chart.update();
    }
  }

  onMount(() => {
    renderChart(activeChart);
    return () => {
      if (chart) chart.destroy();
    };
  });

  // reactive update when activeChart changes
  $: if (chart) {
    renderChart(activeChart);
  }
</script>

<div class="p-4 md:p-8 max-w-5xl mx-auto">

  <!-- Profile -->
  <div class="flex flex-col items-center mt-6">
    <img src={creator.avatar} alt="avatar" class="w-20 h-20 rounded-full shadow" />
    <h2 class="mt-2 text-lg font-bold">{creator.name}</h2>
    <p class="text-gray-500">{creator.username}</p>

    <button
      class="group w-full mt-4 px-6 py-4 rounded-xl bg-orange-500 text-white font-semibold flex items-center justify-center gap-2
             transform transition duration-200 ease-out hover:-translate-y-1 hover:shadow-lg active:scale-95 focus:outline-none focus:ring-2 focus:ring-orange-300 motion-safe:transform-gpu"
      aria-label="เพิ่มหนังสือใหม่"
    >
      <Plus class="w-5 h-5 inline-block mr-2 transition-transform duration-200 ease-out group-hover:translate-x-1 group-active:scale-90" />
      เพิ่มหนังสือใหม่
    </button>
  </div>

  <!-- Overview -->
  <section class="mt-8">
    <h3 class="text-xl font-bold mb-4">Overview</h3>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      {#each stats as s}
        <div class="group bg-white shadow rounded-xl p-4 relative text-left transform transition-transform duration-300 ease-out hover:-translate-y-2 hover:scale-105 hover:rotate-1 hover:shadow-2xl motion-safe:transform-gpu cursor-pointer" style="transition-timing-function: cubic-bezier(0.22,1,0.36,1);">
          <div class="absolute top-3 right-3">
            <div class="w-10 h-10 bg-purple-100 text-purple-600 rounded-[8px] flex items-center justify-center transform transition duration-400 group-hover:-translate-y-1 group-hover:rotate-12 shadow-sm group-hover:shadow-md">
              <Plane class="w-4 h-4 transform transition-transform duration-300 group-hover:scale-110" aria-hidden="true" />
            </div>
          </div>
          <p class="font-semibold">{s.label}</p>
          <p class="text-2xl font-bold mt-2">{s.value.toLocaleString()}</p>
          <div class="flex items-center gap-1 text-green-600 text-sm mt-1">
            <ChevronUp class="w-4 h-4 transform transition-transform duration-300 group-hover:-translate-y-1" />
            <span>8.5% Up from yesterday</span>
          </div>
        </div>
      {/each}
    </div>
  </section>

  <!-- Chart -->
  <section class="mt-8">
    <div class="flex justify-between items-center">
      <h3 class="text-xl font-bold">Sales</h3>
      <button
        class="ml-2 rounded-full bg-orange-500 text-white text-sm font-semibold px-4 py-2
               transform transition duration-200 ease-out hover:-translate-y-1 hover:scale-105 hover:shadow-lg
               hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-orange-300 motion-safe:transform-gpu group"
      >
        <Download class="w-4 h-4 inline-block mr-1 transition-transform duration-200 ease-out group-hover:-translate-y-1 group-hover:rotate-12" />
        Export to .xlsx
      </button>
    </div>

    <div class="mt-3 w-full bg-white rounded-lg shadow-sm p-4 md:p-6 chart-panel">
      <canvas bind:this={chartCanvas} class="w-full h-64"></canvas>
    </div>

    <!-- Pagination buttons -->
    <div class="flex justify-center gap-2 mt-4">
      {#each charts as _, i}
        <button
          class="group w-8 h-8 rounded-full flex items-center justify-center transform transition-all duration-300
                 hover:-translate-y-1 hover:scale-110 hover:rotate-3 hover:shadow-lg
                 {i === activeChart ? 'bg-orange-500 text-white ring-2 ring-orange-200' : 'bg-gray-200 text-gray-700'} focus:outline-none focus:ring-2 focus:ring-orange-300"
          on:click={() => activeChart = i}
          aria-pressed={i === activeChart}
          aria-label={`Go to chart ${i + 1}`}
        >
          <span class="inline-block transition-transform duration-300 group-hover:-translate-y-1 group-hover:scale-105">
            {i + 1}
          </span>
        </button>
      {/each}
    </div>
  </section>

  <!-- Book Manager -->
  <section class="mt-8">
    <h3 class="text-xl font-bold mb-4">Book Manager</h3>
    <div class="space-y-4">
      {#each books as b, i}
        <div
          class="book-card flex items-center bg-white rounded-xl p-4 shadow transform-gpu transition-all duration-300 cursor-pointer"
          style="animation-delay: {i * 60}ms;"
          aria-label={`Book ${b.title}`}
        >
          <div class="cover w-16 h-20 bg-pink-400 rounded-md flex-shrink-0 flex items-center justify-center overflow-hidden">
            <span class="text-white font-semibold text-sm">Cover</span>
          </div>

          <div class="ml-4 flex-1">
            <div class="flex items-start justify-between gap-4">
              <h4 class="font-bold text-gray-900">{b.title}</h4>
              <span class="badge inline-block bg-green-200 text-green-700 text-xs px-2 py-1 rounded mt-1">สาธารณะ</span>
            </div>

            <div class="flex gap-4 text-sm mt-2 text-gray-600 items-center">
              <span class="info-item flex items-center">
                <span class="icon-wrapper" aria-hidden="true">
                  <CircleDollarSign class="w-4 h-4" />
                </span>
                <span>{b.price}</span>
              </span>

              <span class="info-item flex items-center">
                <span class="icon-wrapper" aria-hidden="true">
                  <BookOpenCheck class="w-4 h-4" />
                </span>
                <span>{b.pages}</span>
              </span>

              <span class="info-item flex items-center">
                <span class="icon-wrapper" aria-hidden="true">
                  <MessageCircle class="w-4 h-4" />
                </span>
                <span>{b.comments}</span>
              </span>
            </div>
          </div>
        </div>
      {/each}
    </div>
  </section>
</div>

<style>
  .chart-panel {
    animation: slideFadeIn 320ms ease-out;
  }
  @keyframes slideFadeIn {
    from { transform: translateY(8px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
  }

  .book-card {
    will-change: transform, opacity;
    animation: popIn 360ms cubic-bezier(.22,.9,.27,1) both;
    box-shadow: 0 6px 14px rgba(15,23,42,0.06);
  }
  .book-card:hover {
    transform: translateY(-6px) scale(1.01) rotate(-0.4deg);
    box-shadow: 0 18px 30px rgba(15,23,42,0.12);
  }
  @keyframes popIn {
    from { transform: translateY(10px) scale(.995); opacity: 0; }
    to   { transform: translateY(0)     scale(1);     opacity: 1; }
  }

  .icon-wrapper {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 1.125rem;
    height: 1.125rem;
    margin-right: 0.5rem;
    flex-shrink: 0;
    color: #4b5563;
  }
  .icon-wrapper svg {
    display: block;
    width: 1rem;
    height: 1rem;
    transform-origin: center;
    animation: floatIcon 3.6s ease-in-out infinite;
  }
  @keyframes floatIcon {
    0%   { transform: translateY(0) rotate(0deg); }
    50%  { transform: translateY(-3px) rotate(-3deg); }
    100% { transform: translateY(0) rotate(0deg); }
  }
  .book-card:focus-visible {
    outline: 3px solid rgba(250, 204, 21, 0.18);
    outline-offset: 4px;
  }
  .cover { background-size: cover; background-position: center; }
  .badge { white-space: nowrap; }
</style>