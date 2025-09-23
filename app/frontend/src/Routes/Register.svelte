<script>
  import { createEventDispatcher } from "svelte";
  import { register } from "../lib/api";

  let username = "";
  let email = "";
  let password = "";
  let error = "";
  let success = "";

  const dispatch = createEventDispatcher();

  async function handleRegister() {
    try {
      await register({ username, email, password });
      success = "Registration successful! Please login.";
      error = "";
      setTimeout(() => {
        dispatch("navigate", "login");
      }, 1500);
    } catch (err) {
      error = err.message;
    }
  }
</script>

<div class="flex justify-center items-center h-screen bg-gray-100">
  <div class="w-full max-w-md bg-white p-8 rounded-lg shadow-md">
    <h2 class="text-2xl font-bold mb-6 text-center">Register</h2>

    {#if error}
      <p class="text-red-500 text-sm mb-4">{error}</p>
    {/if}
    {#if success}
      <p class="text-green-500 text-sm mb-4">{success}</p>
    {/if}

    <input
      type="text"
      placeholder="Username"
      bind:value={username}
      class="w-full mb-4 p-2 border rounded"
    />
    <input
      type="email"
      placeholder="Email"
      bind:value={email}
      class="w-full mb-4 p-2 border rounded"
    />
    <input
      type="password"
      placeholder="Password"
      bind:value={password}
      class="w-full mb-4 p-2 border rounded"
    />

    <button
      on:click={handleRegister}
      class="w-full bg-green-500 hover:bg-green-600 text-white py-2 px-4 rounded"
    >
      Register
    </button>

    <p class="mt-4 text-sm text-center">
      Already have an account?
      <a href="#" class="text-blue-500" on:click={() => dispatch("navigate", "login")}>
        Login
      </a>
    </p>
  </div>
</div>