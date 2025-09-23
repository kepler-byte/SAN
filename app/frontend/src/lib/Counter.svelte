<script>
  let count = $state(0)
  const increment = () => {
    count += 1
  }

  console.log("Counter component loaded")
</script>

<button onclick={increment}>
  count is {count}
</button>

-- hidden --
