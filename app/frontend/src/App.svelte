<script>
  import Router, { link } from 'svelte-spa-router';

  import Home from './Pages/Home.svelte';
  import Payment from './Pages/Payment.svelte';
  import Bookstore from './Pages/Bookstore.svelte';
  import Usersettings from './Pages/Usersettings.svelte';
  import NotFound from './Pages/NotFound.svelte';

  const routes = {
    '/': Home,
    '/Home': Home,
    '/Bookstore': Bookstore,
    '/Payment': Payment,
    '/Settings': Usersettings,

    "*": NotFound
  }; 
</script>

<nav>
  <a href="#/Home" use:link>Home</a>
  <a href="#/Bookstore" use:link>Bookstore</a>
  <a href="#/Payment" use:link>Payment</a>
  <a href="#/Settings" use:link>Settings</a>
</nav>

<Router {routes} prefix="" />