<!-- Tooltip attachment using tippy.js -->
<script lang="ts">
  import type { Attachment } from 'svelte/attachments';
  import tippy from 'tippy.js';

  let content = $state('Edit this tooltip');

  function tooltip(content: string, placement: 'top' | 'bottom' | 'left' | 'right' = 'top'): Attachment {
    return (element) => {
      const instance = tippy(element, { content, placement });
      return () => instance.destroy();
    };
  }
</script>

<input bind:value={content} placeholder="Tooltip text" />

<!-- Attachment re-creates tooltip when content or placement changes -->
<button {@attach tooltip(content)}>
  Hover for tooltip
</button>

<!-- Multiple attachments -->
<button
  {@attach tooltip('Top tooltip', 'top')}
  {@attach tooltip('Bottom tooltip', 'bottom')}
>
  Two tooltips
</button>

<!-- Conditional -->
<button {@attach content.length > 0 && tooltip(content)}>
  Conditional tooltip
</button>
