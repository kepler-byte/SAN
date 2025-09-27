// FlipBookViewer.svelte
<script>
  import { onMount, onDestroy } from 'svelte';
  import PageFlip from 'page-flip';

  export let pdfUrl = '';
  export let bookTitle = '';
  export let onClose = () => {};

  let flipBookContainer;
  let flipBook = null;
  let pages = [];
  let loading = true;
  let error = null;
  let currentPage = 1;
  let totalPages = 0;

  // PDF.js setup
  let pdfjsLib;

  onMount(async () => {
    try {
      // Load PDF.js
      const script = document.createElement('script');
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js';
      script.onload = () => {
        pdfjsLib = window.pdfjsLib;
        loadPDF();
      };
      document.head.appendChild(script);
    } catch (err) {
      console.error('Failed to load PDF.js:', err);
      error = 'ไม่สามารถโหลด PDF reader ได้';
      loading = false;
    }
  });

  onDestroy(() => {
    if (flipBook) {
      flipBook.destroy();
    }
    // Clean up any created object URLs
    pages.forEach(page => {
      if (page.imageUrl) {
        URL.revokeObjectURL(page.imageUrl);
      }
    });
  });

  async function loadPDF() {
    if (!pdfUrl || !pdfjsLib) return;

    try {
      loading = true;
      error = null;

      // Convert blob URL to ArrayBuffer
      const response = await fetch(pdfUrl);
      const arrayBuffer = await response.arrayBuffer();
      
      // Load PDF
      const pdf = await pdfjsLib.getDocument(arrayBuffer).promise;
      totalPages = pdf.numPages;
      
      // Convert each page to image
      const pagePromises = [];
      for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
        pagePromises.push(convertPageToImage(pdf, pageNum));
      }
      
      pages = await Promise.all(pagePromises);
      
      // Initialize FlipBook after pages are ready
      setTimeout(() => {
        initFlipBook();
        loading = false;
      }, 100);

    } catch (err) {
      console.error('Error loading PDF:', err);
      error = 'ไม่สามารถโหลด PDF ได้: ' + err.message;
      loading = false;
    }
  }

  async function convertPageToImage(pdf, pageNum) {
    const page = await pdf.getPage(pageNum);
    const scale = 2; // Higher scale for better quality
    const viewport = page.getViewport({ scale });

    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.height = viewport.height;
    canvas.width = viewport.width;

    await page.render({
      canvasContext: context,
      viewport: viewport
    }).promise;

    return {
      pageNum,
      imageUrl: canvas.toDataURL('image/jpeg', 0.9),
      width: viewport.width / scale,
      height: viewport.height / scale
    };
  }

  function initFlipBook() {
    if (!flipBookContainer || pages.length === 0) return;

    try {
      // Clear container
      flipBookContainer.innerHTML = '';

      // Calculate optimal size
      const containerRect = flipBookContainer.getBoundingClientRect();
      const maxWidth = Math.min(containerRect.width - 40, 800);
      const pageWidth = maxWidth / 2; // Two pages side by side
      const pageHeight = pages[0] ? (pages[0].height * pageWidth) / pages[0].width : 600;

      flipBook = new PageFlip(flipBookContainer, {
        width: pageWidth,
        height: pageHeight,
        size: "stretch",
        minWidth: 200,
        maxWidth: 400,
        minHeight: 200,
        maxHeight: 800,
        maxShadowOpacity: 0.5,
        showCover: true,
        mobileScrollSupport: false,
        swipeDistance: 30,
        clickEventForward: true,
        usePortrait: window.innerWidth < 768,
        startPage: 0,
        drawShadow: true,
        flippingTime: 1000,
        useMouseEvents: true,
        autoSize: true,
        showPageCorners: true,
        disableFlipByClick: false
      });

      // Add pages to flipbook
      pages.forEach((page, index) => {
        const pageElement = document.createElement('div');
        pageElement.className = 'page';
        pageElement.innerHTML = `
          <div class="page-content">
            <img src="${page.imageUrl}" alt="Page ${page.pageNum}" />
          </div>
        `;
        flipBook.loadFromHTML([pageElement]);
      });

      // Event listeners
      flipBook.on('flip', (e) => {
        currentPage = e.data + 1;
      });

      flipBook.on('changeOrientation', (e) => {
        flipBook.updateSetting({
          usePortrait: e.data === 'portrait'
        });
      });

    } catch (err) {
      console.error('Error initializing FlipBook:', err);
      error = 'ไม่สามารถสร้าง FlipBook ได้';
    }
  }

  function nextPage() {
    if (flipBook) {
      flipBook.flipNext();
    }
  }

  function prevPage() {
    if (flipBook) {
      flipBook.flipPrev();
    }
  }

  function goToPage(pageNum) {
    if (flipBook && pageNum >= 1 && pageNum <= totalPages) {
      flipBook.flip(pageNum - 1);
    }
  }

  function downloadPDF() {
    if (pdfUrl) {
      const link = document.createElement('a');
      link.href = pdfUrl;
      link.download = `${bookTitle || 'book'}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  }

  function handleKeydown(event) {
    if (event.key === 'Escape') {
      onClose();
    } else if (event.key === 'ArrowLeft') {
      prevPage();
    } else if (event.key === 'ArrowRight') {
      nextPage();
    }
  }
</script>

<svelte:window on:keydown={handleKeydown} />

<div class="flipbook-modal">
  <div class="modal-backdrop" on:click={onClose}></div>
  
  <div class="modal-content">
    <!-- Header -->
    <div class="modal-header">
      <h3 class="book-title">{bookTitle}</h3>
      <div class="header-controls">
        <div class="page-info">
          หน้า {currentPage} จาก {totalPages}
        </div>
        <button class="control-btn" on:click={downloadPDF} title="ดาวน์โหลด">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7,10 12,15 17,10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
        </button>
        <button class="control-btn close-btn" on:click={onClose} title="ปิด">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- FlipBook Container -->
    <div class="flipbook-container">
      {#if loading}
        <div class="loading-container">
          <div class="loading-spinner"></div>
          <p>กำลังโหลด PDF...</p>
        </div>
      {:else if error}
        <div class="error-container">
          <div class="error-icon">⚠️</div>
          <p>{error}</p>
          <button class="retry-btn" on:click={loadPDF}>ลองใหม่</button>
        </div>
      {:else}
        <div bind:this={flipBookContainer} class="flipbook-viewer"></div>
      {/if}
    </div>

    <!-- Controls -->
    <div class="modal-controls">
      <button class="nav-btn" on:click={prevPage} disabled={currentPage <= 1}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <polyline points="15,18 9,12 15,6"/>
        </svg>
        หน้าก่อน
      </button>

      <div class="page-controls">
        <input 
          type="number" 
          min="1" 
          max={totalPages} 
          bind:value={currentPage}
          on:change={() => goToPage(currentPage)}
          class="page-input"
        />
        <span>/ {totalPages}</span>
      </div>

      <button class="nav-btn" on:click={nextPage} disabled={currentPage >= totalPages}>
        หน้าถัดไป
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <polyline points="9,18 15,12 9,6"/>
        </svg>
      </button>
    </div>
  </div>
</div>

<style>
  :global(body) {
    overflow: hidden;
  }

  .flipbook-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: fadeIn 0.3s ease-out;
  }

  .modal-backdrop {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    backdrop-filter: blur(5px);
  }

  .modal-content {
    position: relative;
    background: white;
    border-radius: 12px;
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
    max-width: 95vw;
    max-height: 95vh;
    width: 1000px;
    height: 700px;
    display: flex;
    flex-direction: column;
    animation: slideUp 0.4s ease-out;
    overflow: hidden;
  }

  .modal-header {
    display: flex;
    justify-content: between;
    align-items: center;
    padding: 16px 24px;
    border-bottom: 1px solid #e5e7eb;
    background: #f9fafb;
  }

  .book-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: #111827;
    margin: 0;
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .header-controls {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .page-info {
    font-size: 0.875rem;
    color: #6b7280;
    font-weight: 500;
  }

  .control-btn {
    background: none;
    border: none;
    padding: 8px;
    border-radius: 6px;
    color: #6b7280;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .control-btn:hover {
    background: #e5e7eb;
    color: #374151;
  }

  .close-btn:hover {
    background: #fee2e2;
    color: #dc2626;
  }

  .flipbook-container {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    background: #f3f4f6;
    overflow: hidden;
  }

  .flipbook-viewer {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  :global(.flipbook-viewer .page) {
    background: white;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    border-radius: 4px;
    overflow: hidden;
  }

  :global(.flipbook-viewer .page-content) {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  :global(.flipbook-viewer .page-content img) {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
  }

  .loading-container, .error-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px;
    text-align: center;
  }

  .loading-spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #e5e7eb;
    border-top: 3px solid #3b82f6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 16px;
  }

  .error-container {
    color: #dc2626;
  }

  .error-icon {
    font-size: 3rem;
    margin-bottom: 16px;
  }

  .retry-btn {
    background: #3b82f6;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
    margin-top: 16px;
    transition: background 0.2s ease;
  }

  .retry-btn:hover {
    background: #2563eb;
  }

  .modal-controls {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 24px;
    border-top: 1px solid #e5e7eb;
    background: #f9fafb;
  }

  .nav-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    background: #3b82f6;
    color: white;
    border: none;
    padding: 10px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s ease;
  }

  .nav-btn:hover:not(:disabled) {
    background: #2563eb;
    transform: translateY(-1px);
  }

  .nav-btn:disabled {
    background: #d1d5db;
    color: #9ca3af;
    cursor: not-allowed;
    transform: none;
  }

  .page-controls {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #6b7280;
    font-weight: 500;
  }

  .page-input {
    width: 60px;
    padding: 6px 8px;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    text-align: center;
    font-size: 0.875rem;
  }

  .page-input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(30px) scale(0.95);
    }
    to {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* Mobile responsiveness */
  @media (max-width: 768px) {
    .modal-content {
      width: 100vw;
      height: 100vh;
      max-width: 100vw;
      max-height: 100vh;
      border-radius: 0;
    }

    .modal-header {
      padding: 12px 16px;
    }

    .book-title {
      font-size: 1rem;
    }

    .modal-controls {
      padding: 12px 16px;
      flex-direction: column;
      gap: 12px;
    }

    .nav-btn {
      padding: 12px 20px;
      width: 100%;
      justify-content: center;
    }

    :global(.flipbook-viewer) {
      transform: scale(0.9);
    }
  }
</style>