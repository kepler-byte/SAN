<script>
  import { createEventDispatcher } from "svelte";
  import { login } from "../lib/api";
  import { setAuthToken } from "../lib/auth";

  let username = "";
  let password = "";
  let error = "";

  const dispatch = createEventDispatcher();

  async function handleLogin() {
    try {
      const res = await login({ username, password });
      setAuthToken(res.access_token);
      dispatch("navigate", "dashboard");
    } catch (err) {
      error = err.message;
    }
  }
</script>

<div class="flex justify-center items-center h-screen bg-gray-100">
  <div class="w-full max-w-md bg-white p-8 rounded-lg shadow-md">
    <h2 class="text-2xl font-bold mb-6 text-center">Login</h2>

    {#if error}
      <p class="text-red-500 text-sm mb-4">{error}</p>
    {/if}

    <input
      type="text"
      placeholder="Username"
      bind:value={username}
      class="w-full mb-4 p-2 border rounded"
    />
    <input
      type="password"
      placeholder="Password"
      bind:value={password}
      class="w-full mb-4 p-2 border rounded"
    />

    <button
      on:click={handleLogin}
      class="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded"
    >
      Login
    </button>

    <p class="mt-4 text-sm text-center">
      Don’t have an account?
      <a href="#" class="text-blue-500" on:click={() => dispatch("navigate", "register")}>
        Register
      </a>
    </p>
  </div>
</div>