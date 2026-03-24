<!-- fork() pattern for hover preloading -->
<script lang="ts">
  import { fork } from 'svelte';

  type MenuItem = { label: string; href: string };

  let open = $state(false);
  let items = $state<MenuItem[]>([]);
  let pendingFork: ReturnType<typeof fork> | null = null;

  async function loadMenuItems(): Promise<MenuItem[]> {
    const res = await fetch('/api/menu');
    return res.json();
  }

  // Speculatively load data on hover without affecting DOM
  function preload() {
    pendingFork ??= fork(() => {
      open = true;
      // This triggers async work (loading items)
      // but fork() prevents DOM updates until commit()
    });
  }

  function cancelPreload() {
    pendingFork?.discard();
    pendingFork = null;
  }

  async function openMenu() {
    if (pendingFork) {
      // Data was preloaded — commit instantly
      await pendingFork.commit();
      pendingFork = null;
    }
    open = true;
    if (!items.length) {
      items = await loadMenuItems();
    }
  }
</script>

<button
  onpointerenter={preload}
  onpointerleave={cancelPreload}
  onfocusin={preload}
  onfocusout={cancelPreload}
  onclick={openMenu}
>
  Open menu
</button>

{#if open}
  <svelte:boundary>
    <nav class="menu">
      {#each items as item}
        <a href={item.href}>{item.label}</a>
      {/each}
    </nav>

    {#snippet pending()}
      <nav class="menu">
        <p>Loading...</p>
      </nav>
    {/snippet}
  </svelte:boundary>
{/if}
