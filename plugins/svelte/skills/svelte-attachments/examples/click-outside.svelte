<!-- Click outside attachment for dropdowns/modals -->
<script lang="ts">
  import type { Attachment } from 'svelte/attachments';

  let open = $state(false);

  function clickOutside(callback: () => void): Attachment {
    return (node) => {
      function handleClick(event: MouseEvent) {
        if (!node.contains(event.target as Node)) {
          callback();
        }
      }
      // Use capture to catch events before they're stopped
      document.addEventListener('click', handleClick, true);
      return () => document.removeEventListener('click', handleClick, true);
    };
  }
</script>

<button onclick={() => open = !open}>
  Toggle dropdown
</button>

{#if open}
  <div
    class="dropdown"
    {@attach clickOutside(() => open = false)}
  >
    <p>Click outside to close</p>
    <button onclick={() => console.log('inner click')}>
      Inner button
    </button>
  </div>
{/if}
