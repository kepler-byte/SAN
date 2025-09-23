<script>
  import { authToken } from "./lib/auth";
  import { onMount } from "svelte";

  import Login from "./Routes/Login.svelte";
  import Register from "./Routes/Register.svelte";
  import Home from "./Routes/Home.svelte";

  let page = "login"; // ค่า default

  $: token = $authToken;

  onMount(() => {
    if (token) {
      page = "home";
    }
  });

  function handleNavigate(target) {
    page = target;
  }
</script>

{#if !token}
  {#if page === "login"}
    <Login on:navigate={e => handleNavigate(e.detail)} />
  {:else if page === "register"}
    <Register on:navigate={e => handleNavigate(e.detail)} />
  {/if}
{:else}
  <Home />
{/if}