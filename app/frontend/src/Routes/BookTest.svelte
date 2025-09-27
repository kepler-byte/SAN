<script>
    import { onMount } from 'svelte';
    import { uploadBook, getBookDetail, getCurrentUser, getBookCategories } from '../lib/api.js';

    let isAdmin = true;
    let message = '';
    let bookData = {
        title: '',
        rating: 0,
        description: '',
        category: 'อื่นๆ',
        price: 0
    };
    let coverFile = null;
    let pdfFile = null;  // 🆕 NEW: PDF file
    let bookId = '';
    let fetchedBook = null;
    let error = '';
    let categories = [];
    let loadingCategories = false;
    let uploading = false;  // 🆕 NEW: Upload loading state

    onMount(async () => {
        await loadCategories();
        
        try {
            const user = await getCurrentUser();
            isAdmin = user.role === 'admin';
        } catch (err) {
            console.error('Failed to check admin status:', err);
        }
    });

    async function loadCategories() {
        loadingCategories = true;
        try {
            const response = await getBookCategories();
            categories = response.categories || [];
            if (categories.length === 0) {
                categories = ['อื่นๆ', 'นิยาย', 'บทความ', 'การศึกษา', 'ธุรกิจ', 'เทคโนโลยี'];
            }
        } catch (err) {
            console.error('Failed to load categories:', err);
            categories = ['อื่นๆ', 'นิยาย', 'บทความ', 'การศึกษา', 'ธุรกิจ', 'เทคโนโลยี'];
        } finally {
            loadingCategories = false;
        }
    }

    async function handleUpload() {
        error = '';
        message = '';
        uploading = true;
        
        try {
            // 🆕 UPDATED: Pass PDF file to upload function
            const response = await uploadBook(bookData, coverFile, pdfFile);
            message = `หนังสือถูกอัปโหลดสำเร็จ! ID: ${response.id}`;
            
            if (response.has_pdf) {
                message += ' ✅ PDF อัปโหลดสำเร็จ';
            } else if (pdfFile) {
                message += ' ⚠️ PDF อัปโหลดไม่สำเร็จ';
            }
            
            if (response.has_cover) {
                message += ' ✅ รูปปกอัปโหลดสำเร็จ';
            }
            
            // Reset form
            bookData = { title: '', rating: 0, description: '', category: 'อื่นๆ', price: 0 };
            coverFile = null;
            pdfFile = null;
            
            // Reset file inputs
            const coverInput = document.getElementById('cover');
            const pdfInput = document.getElementById('pdf');
            if (coverInput) coverInput.value = '';
            if (pdfInput) pdfInput.value = '';
        } catch (err) {
            error = err.message;
        } finally {
            uploading = false;
        }
    }

    async function handleFetch() {
        error = '';
        message = '';
        fetchedBook = null;
        try {
            fetchedBook = await getBookDetail(bookId);
            message = 'ดึงข้อมูลหนังสือสำเร็จ!';
        } catch (err) {
            error = err.message;
        }
    }

    function handleCoverFileChange(event) {
        coverFile = event.target.files[0];
    }

    // 🆕 NEW: PDF file change handler
    function handlePdfFileChange(event) {
        pdfFile = event.target.files[0];
        
        // Validate PDF file size (optional)
        if (pdfFile && pdfFile.size > 50 * 1024 * 1024) { // 50MB limit
            alert('ไฟล์ PDF ใหญ่เกินไป (สูงสุด 50MB)');
            pdfFile = null;
            event.target.value = '';
        }
    }

    // 🆕 NEW: Format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
</script>

<div class="max-w-2xl mx-auto p-6 bg-white shadow-lg rounded-lg mt-8">
    <h1 class="text-3xl font-bold mb-6 text-center text-gray-800">Book API Test Page (GridFS)</h1>

    {#if error}
        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            <strong>เกิดข้อผิดพลาด:</strong> {error}
        </div>
    {/if}
    {#if message}
        <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
            {message}
        </div>
    {/if}

    {#if isAdmin}
        <section class="mb-8">
            <h2 class="text-2xl font-semibold mb-4 text-gray-700">อัปโหลดหนังสือ (เฉพาะแอดมิน)</h2>
            
            <!-- 🆕 NEW: GridFS Info -->
            <div class="bg-blue-50 border border-blue-200 rounded-md p-3 mb-4">
                <p class="text-sm text-blue-700">
                    <strong>GridFS Storage:</strong> ไฟล์จะถูกเก็บใน MongoDB GridFS แทนการเก็บในโฟลเดอร์
                </p>
            </div>
            
            <form on:submit|preventDefault={handleUpload} class="space-y-4">
                <div>
                    <label for="title" class="block text-sm font-medium text-gray-700">ชื่อหนังสือ *</label>
                    <input 
                        id="title" 
                        type="text" 
                        bind:value={bookData.title} 
                        required 
                        class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500" 
                        placeholder="กรุณาใส่ชื่อหนังสือ"
                        disabled={uploading}
                    />
                </div>

                <div class="bg-blue-50 border border-blue-200 rounded-md p-3">
                    <p class="text-sm text-blue-700">
                        <strong>หมายเหตุ:</strong> ผู้เขียนจะถูกกำหนดเป็นชื่อผู้ใช้ของคุณโดยอัตโนมัติ
                    </p>
                </div>

                <div>
                    <label for="category" class="block text-sm font-medium text-gray-700">หมวดหมู่ *</label>
                    {#if loadingCategories}
                        <div class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 bg-gray-100 text-gray-500">
                            กำลังโหลดหมวดหมู่...
                        </div>
                    {:else}
                        <select 
                            id="category" 
                            bind:value={bookData.category} 
                            required
                            class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
                            disabled={uploading}
                        >
                            {#each categories as category}
                                <option value={category}>{category}</option>
                            {/each}
                        </select>
                    {/if}
                </div>
                
                <div>
                    <label for="rating" class="block text-sm font-medium text-gray-700">คะแนนความนิยม (0-5) *</label>
                    <input 
                        id="rating" 
                        type="number" 
                        bind:value={bookData.rating} 
                        step="0.1" 
                        min="0" 
                        max="5" 
                        required 
                        class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500" 
                        placeholder="เช่น 4.5"
                        disabled={uploading}
                    />
                </div>

                <div>
                    <label for="price" class="block text-sm font-medium text-gray-700">ราคา (Points) *</label>
                    <input 
                        id="price" 
                        type="number" 
                        bind:value={bookData.price} 
                        min="0" 
                        step="1"
                        required 
                        class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500" 
                        placeholder="0"
                        disabled={uploading}
                    />
                    <div class="mt-1 flex items-center space-x-2">
                        <span class="text-xs text-gray-600">
                            {#if bookData.price === 0}
                                🆓 ฟรี
                            {:else if bookData.price <= 10}
                                💰 ราคาถูก
                            {:else if bookData.price <= 50}
                                💎 ราคาปานกลาง
                            {:else}
                                ⭐ ราคาพรีเมียม
                            {/if}
                        </span>
                        <span class="text-xs text-blue-600">({bookData.price} Points)</span>
                    </div>
                    <p class="text-xs text-gray-500 mt-1">ใส่ 0 หากต้องการให้ฟรี หรือใส่จำนวน Points ที่ต้องการ</p>
                </div>
                
                <div>
                    <label for="description" class="block text-sm font-medium text-gray-700">คำอธิบาย *</label>
                    <textarea 
                        id="description" 
                        bind:value={bookData.description} 
                        required 
                        rows="4"
                        class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500" 
                        placeholder="เขียนคำอธิบายเกี่ยวกับหนังสือเล่มนี้..."
                        disabled={uploading}
                    ></textarea>
                </div>
                
                <div>
                    <label for="cover" class="block text-sm font-medium text-gray-700">รูปปกหนังสือ (ไม่บังคับ)</label>
                    <input 
                        id="cover" 
                        type="file" 
                        accept="image/*" 
                        on:change={handleCoverFileChange} 
                        class="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100" 
                        disabled={uploading}
                    />
                    <p class="text-xs text-gray-500 mt-1">รองรับไฟล์รูปภาพเท่านั้น (JPG, PNG, GIF)</p>
                    {#if coverFile}
                        <p class="text-xs text-green-600 mt-1">✅ เลือกไฟล์: {coverFile.name} ({formatFileSize(coverFile.size)})</p>
                    {/if}
                </div>

                <!-- 🆕 NEW: PDF File Upload -->
                <div>
                    <label for="pdf" class="block text-sm font-medium text-gray-700">ไฟล์ PDF (ไม่บังคับ)</label>
                    <input 
                        id="pdf" 
                        type="file" 
                        accept=".pdf" 
                        on:change={handlePdfFileChange} 
                        class="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100" 
                        disabled={uploading}
                    />
                    <p class="text-xs text-gray-500 mt-1">รองรับไฟล์ PDF เท่านั้น (สูงสุด 50MB)</p>
                    {#if pdfFile}
                        <p class="text-xs text-green-600 mt-1">📄 เลือกไฟล์: {pdfFile.name} ({formatFileSize(pdfFile.size)})</p>
                    {/if}
                </div>
                
                <button 
                    type="submit" 
                    class="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 font-medium transition-colors"
                    class:opacity-50={uploading}
                    class:cursor-not-allowed={uploading}
                    disabled={uploading}
                >
                    {#if uploading}
                        <div class="flex items-center justify-center gap-2">
                            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                            <span>กำลังอัปโหลด...</span>
                        </div>
                    {:else}
                        อัปโหลดหนังสือ
                    {/if}
                </button>
            </form>
        </section>
    {:else}
        <div class="bg-blue-100 border border-blue-400 text-blue-700 px-4 py-3 rounded mb-4">
            คุณต้องเป็นแอดมินเพื่ออัปโหลดหนังสือ
        </div>
    {/if}

    <section>
        <h2 class="text-2xl font-semibold mb-4 text-gray-700">ดูรายละเอียดหนังสือ</h2>
        <form on:submit|preventDefault={handleFetch} class="space-y-4 mb-4">
            <div>
                <label for="bookId" class="block text-sm font-medium text-gray-700">รหัสหนังสือ (Book ID) *</label>
                <input 
                    id="bookId" 
                    type="text" 
                    bind:value={bookId} 
                    required 
                    class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500" 
                    placeholder="กรุณาใส่รหัสหนังสือ"
                />
            </div>
            <button 
                type="submit" 
                class="w-full bg-green-600 text-white py-3 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 font-medium transition-colors"
            >
                ดึงข้อมูลหนังสือ
            </button>
        </form>

        {#if fetchedBook}
            <div class="bg-gray-50 border border-gray-200 rounded-lg p-6 shadow-sm">
                <h3 class="text-xl font-bold mb-3 text-gray-800">{fetchedBook.title}</h3>
                <div class="grid grid-cols-1 gap-2 mb-4">
                    <p class="text-gray-700"><strong>ผู้เขียน:</strong> {fetchedBook.author}</p>
                    <p class="text-gray-700"><strong>คะแนน:</strong> ⭐ {fetchedBook.rating}/5</p>
                    <p class="text-gray-700"><strong>ราคา:</strong> 
                        {#if fetchedBook.price === 0}
                            <span class="inline-block bg-green-100 text-green-800 text-sm px-2 py-1 rounded-full ml-1">
                                🆓 ฟรี
                            </span>
                        {:else}
                            <span class="inline-block bg-yellow-100 text-yellow-800 text-sm px-2 py-1 rounded-full ml-1">
                                💰 {fetchedBook.price} Points
                            </span>
                        {/if}
                    </p>
                    <p class="text-gray-700"><strong>หมวดหมู่:</strong> 
                        <span class="inline-block bg-blue-100 text-blue-800 text-sm px-2 py-1 rounded-full ml-1">
                            {fetchedBook.category || 'ไม่ระบุ'}
                        </span>
                    </p>
                    
                    <!-- 🆕 NEW: GridFS File Status -->
                    <div class="flex gap-4 mt-2">
                        <p class="text-gray-700">
                            <strong>PDF:</strong> 
                            {#if fetchedBook.has_pdf}
                                <span class="inline-block bg-green-100 text-green-800 text-sm px-2 py-1 rounded-full ml-1">
                                    ✅ มี PDF
                                </span>
                            {:else}
                                <span class="inline-block bg-red-100 text-red-800 text-sm px-2 py-1 rounded-full ml-1">
                                    ❌ ไม่มี PDF
                                </span>
                            {/if}
                        </p>
                        <p class="text-gray-700">
                            <strong>รูปปก:</strong> 
                            {#if fetchedBook.has_cover}
                                <span class="inline-block bg-green-100 text-green-800 text-sm px-2 py-1 rounded-full ml-1">
                                    ✅ มีรูปปก
                                </span>
                            {:else}
                                <span class="inline-block bg-red-100 text-red-800 text-sm px-2 py-1 rounded-full ml-1">
                                    ❌ ไม่มีรูปปก
                                </span>
                            {/if}
                        </p>
                    </div>
                    
                    {#if fetchedBook.file_size}
                        <p class="text-gray-700"><strong>ขนาดไฟล์ PDF:</strong> {formatFileSize(fetchedBook.file_size)}</p>
                    {/if}
                    
                    <p class="text-gray-700"><strong>คำอธิบาย:</strong></p>
                    <p class="text-gray-600 bg-white p-3 rounded border italic">{fetchedBook.description}</p>
                </div>
                
                <!-- 🆕 NEW: GridFS Cover Display -->
                {#if fetchedBook.has_cover}
                    <div class="mb-4">
                        <p class="text-gray-700 font-medium mb-2">รูปปกหนังสือ (จาก GridFS):</p>
                        <img 
                            src="/api/books/{fetchedBook.id}/cover" 
                            alt="Book Cover" 
                            class="max-w-xs rounded-lg shadow-md border"
                            on:error={() => console.log('Failed to load cover image from GridFS')}
                        />
                    </div>
                {/if}
                
                <div class="text-gray-500 text-sm pt-2 border-t border-gray-200">
                    <p><strong>สร้างเมื่อ:</strong> {new Date(fetchedBook.created_at).toLocaleString('th-TH')}</p>
                    <p><strong>รหัสหนังสือ:</strong> {fetchedBook.id}</p>
                </div>
            </div>
        {/if}
    </section>
</div>