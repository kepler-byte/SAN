<script>
  import { onMount, onDestroy } from 'svelte';
  import { X, Users, BookOpen, Heart, UserPlus, UserCheck } from '@lucide/svelte';

  export let creatorUsername = '';
  export let isOpen = false;
  export let onClose = () => {};

  let loading = true;
  let error = null;
  let isFollowing = false;
  let followLoading = false;
  let creatorData = {
    followers_count: 0,
    following_count: 0,
    books_count: 0,
    total_sales: 0,
    profile_picture: null
  };

  // reactive watcher — load data whenever modal opens with a username
  $: if (isOpen && creatorUsername) {
    console.log('Popover opened for:', creatorUsername);
    loadCreatorData();
  }

  async function loadCreatorData() {
    try {
      loading = true;
      error = null;

      const token = localStorage.getItem('token');
      console.log('Stored token:', token);
      if (!token) {
        throw new Error('No authentication token found');
      }

      console.log('Fetching creator profile for:', creatorUsername);
      const url = `http://127.0.0.1:8000/creator/profile/${encodeURIComponent(creatorUsername)}`;
      console.log('Request URL:', url);

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      console.log('Response status:', response.status);
      const responseText = await response.text();
      console.log('Response text:', responseText);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${responseText}`);
      }

      const creatorProfile = JSON.parse(responseText);
      console.log('Creator profile loaded successfully:', creatorProfile);
      
      creatorData = {
        followers_count: creatorProfile.followers_count ?? 0,
        following_count: creatorProfile.following_count ?? 0,
        books_count: creatorProfile.total_books ?? 0,
        total_sales: creatorProfile.total_sales ?? 0,
        profile_picture: creatorProfile.profile_picture ?? null
      };
      
      isFollowing = creatorProfile.is_following ?? false;
      console.log('Creator data updated:', creatorData);
    } catch (err) {
      error = err.message || 'Failed to load creator data';
      console.error('Full error object:', err);
    } finally {
      loading = false;
    }
  }

  function handleClose() {
    isOpen = false;
    onClose();
  }

  function handleBackdropClick(e) {
    if (e.target === e.currentTarget) handleClose();
  }

  function handleKeydown(e) {
    if (e.key === 'Escape' && isOpen) handleClose();
  }

  async function handleFollowToggle() {
    try {
      followLoading = true;
      const token = localStorage.getItem('token');
      if (!token) throw new Error('No authentication token found');

      const endpoint = isFollowing 
        ? `http://127.0.0.1:8000/creator/unfollow/${encodeURIComponent(creatorUsername)}`
        : `http://127.0.0.1:8000/creator/follow/${encodeURIComponent(creatorUsername)}`;
      const method = isFollowing ? 'DELETE' : 'POST';

      const response = await fetch(endpoint, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to update follow status');
      }

      isFollowing = !isFollowing;
      creatorData.followers_count += isFollowing ? 1 : -1;
      if (creatorData.followers_count < 0) creatorData.followers_count = 0;
    } catch (err) {
      error = err.message || 'Failed to update follow status';
      console.error('Error toggling follow:', err);
    } finally {
      followLoading = false;
    }
  }

  onMount(() => {
    console.log('CreatorPopover mounted');
  });

  onDestroy(() => {
    window.removeEventListener('keydown', handleKeydown);
  });
</script>

<svelte:window on:keydown={handleKeydown} />

{#if isOpen}
  <div 
    class="fixed inset-0 z-40 bg-black bg-opacity-40 transition-opacity duration-200"
    on:click={handleBackdropClick}
  />

  <div 
    class="fixed z-50 bg-white rounded-xl shadow-2xl overflow-hidden animate-popover"
    style="width: 320px; top: 50%; left: 50%; transform: translate(-50%, -50%);"
  >
    <!-- Header -->
    <div class="relative bg-gradient-to-r from-orange-400 to-orange-500 px-6 py-6 text-white">
      <button
        class="absolute top-3 right-3 p-1 hover:bg-orange-600 rounded-full transition-colors"
        on:click={handleClose}
        title="Close"
      >
        <X class="w-5 h-5" />
      </button>

      <!-- Profile Picture and Info -->
      <div class="flex items-center gap-4">
        <div class="flex-shrink-0">
          {#if creatorData.profile_picture}
            <img 
              src={creatorData.profile_picture} 
              alt={creatorUsername}
              class="w-16 h-16 rounded-full object-cover border-3 border-white"
            />
          {:else}
            <div class="w-16 h-16 rounded-full bg-orange-600 border-3 border-white flex items-center justify-center">
              <span class="text-2xl font-bold">{creatorUsername.charAt(0).toUpperCase()}</span>
            </div>
          {/if}
        </div>

        <div class="flex-1 min-w-0">
          <h2 class="text-lg font-bold truncate">{creatorUsername}</h2>
          <p class="text-xs text-orange-100">Creator Profile</p>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="p-6">
      {#if loading}
        <div class="flex flex-col items-center justify-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-400 mb-4"></div>
          <p class="text-sm text-gray-600">Loading profile...</p>
        </div>
      {:else if error}
        <div class="text-center py-8">
          <p class="text-red-500 text-sm mb-2">Error loading profile</p>
          <p class="text-gray-500 text-xs mb-4">{error}</p>
          <button
            class="px-4 py-2 bg-orange-500 text-white rounded-lg text-sm hover:bg-orange-600 transition-colors"
            on:click={loadCreatorData}
          >
            Try Again
          </button>
        </div>
      {:else}
        <div class="space-y-4">
          <div class="flex items-center gap-3 p-3 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
            <Users class="w-5 h-5 text-blue-600" />
            <div class="flex-1 min-w-0">
              <p class="text-xs text-gray-600 font-medium">Followers</p>
              <p class="text-lg font-bold text-blue-600">{creatorData.followers_count.toLocaleString()}</p>
            </div>
          </div>

          <div class="flex items-center gap-3 p-3 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors">
            <Heart class="w-5 h-5 text-purple-600" />
            <div class="flex-1 min-w-0">
              <p class="text-xs text-gray-600 font-medium">Following</p>
              <p class="text-lg font-bold text-purple-600">{creatorData.following_count.toLocaleString()}</p>
            </div>
          </div>

          <div class="flex items-center gap-3 p-3 bg-green-50 rounded-lg hover:bg-green-100 transition-colors">
            <BookOpen class="w-5 h-5 text-green-600" />
            <div class="flex-1 min-w-0">
              <p class="text-xs text-gray-600 font-medium">Books Uploaded</p>
              <p class="text-lg font-bold text-green-600">{creatorData.books_count.toLocaleString()}</p>
            </div>
          </div>
        </div>

        <div class="mt-6 pt-4 border-t border-gray-200">
          <p class="text-xs text-gray-500 text-center">
            Total Sales: <span class="font-semibold text-gray-700">{creatorData.total_sales.toLocaleString()} Points</span>
          </p>
        </div>

        <button
          class="w-full mt-6 px-4 py-3 rounded-lg font-semibold text-white transition-all duration-200 flex items-center justify-center gap-2"
          class:bg-orange-500={!isFollowing}
          class:hover:bg-orange-600={!isFollowing}
          class:bg-gray-400={isFollowing}
          class:hover:bg-gray-500={isFollowing}
          class:opacity-50={followLoading}
          class:cursor-not-allowed={followLoading}
          on:click={handleFollowToggle}
          disabled={followLoading}
        >
          {#if followLoading}
            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            <span>{isFollowing ? 'Unfollowing...' : 'Following...'}</span>
          {:else if isFollowing}
            <UserCheck class="w-4 h-4" />
            <span>Following</span>
          {:else}
            <UserPlus class="w-4 h-4" />
            <span>Follow Creator</span>
          {/if}
        </button>
      {/if}
    </div>
  </div>
{/if}

<style>
  @keyframes popover {
    from {
      opacity: 0;
      transform: translate(-50%, -50%) scale(0.95);
    }
    to {
      opacity: 1;
      transform: translate(-50%, -50%) scale(1);
    }
  }

  .animate-popover {
    animation: popover 0.2s ease-out;
  }
</style>