# shadcn-svelte Component Patterns

## Import Convention

Components are imported from their barrel export:

```ts
import * as Dialog from "$lib/components/ui/dialog/index.js";
import { Button } from "$lib/components/ui/button/index.js";
import { Input } from "$lib/components/ui/input/index.js";
```

## Dialog

```svelte
<Dialog.Root>
  <Dialog.Trigger>
    {#snippet child({ props })}
      <Button {...props} variant="outline">Edit</Button>
    {/snippet}
  </Dialog.Trigger>
  <Dialog.Content class="sm:max-w-[425px]">
    <Dialog.Header>
      <Dialog.Title>Edit Profile</Dialog.Title>
      <Dialog.Description>Make changes to your profile.</Dialog.Description>
    </Dialog.Header>
    <!-- content -->
    <Dialog.Footer>
      <Dialog.Close>
        {#snippet child({ props })}
          <Button {...props} variant="outline">Cancel</Button>
        {/snippet}
      </Dialog.Close>
      <Button>Save</Button>
    </Dialog.Footer>
  </Dialog.Content>
</Dialog.Root>
```

### Controlled Dialog

```svelte
<script>
  let open = $state(false);
</script>

<Dialog.Root bind:open>
  <Dialog.Content><!-- ... --></Dialog.Content>
</Dialog.Root>

<Button onclick={() => open = true}>Open</Button>
```

## Sheet (Side Panel)

```svelte
<Sheet.Root>
  <Sheet.Trigger>Open</Sheet.Trigger>
  <Sheet.Content side="right">  <!-- "left" | "right" | "top" | "bottom" -->
    <Sheet.Header>
      <Sheet.Title>Settings</Sheet.Title>
      <Sheet.Description>Configure preferences.</Sheet.Description>
    </Sheet.Header>
    <div class="py-4"><!-- content --></div>
    <Sheet.Footer>
      <Sheet.Close>Done</Sheet.Close>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>
```

## Command Palette (Cmd+K)

```svelte
<script lang="ts">
  import * as Command from "$lib/components/ui/command/index.js";
  let open = $state(false);

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      open = !open;
    }
  }
</script>

<svelte:document onkeydown={handleKeydown} />

<Command.Dialog bind:open>
  <Command.Input placeholder="Type a command..." />
  <Command.List>
    <Command.Empty>No results.</Command.Empty>
    <Command.Group heading="Navigation">
      <Command.Item onSelect={() => goto('/dashboard')}>Dashboard</Command.Item>
      <Command.Item onSelect={() => goto('/settings')}>Settings</Command.Item>
    </Command.Group>
    <Command.Separator />
    <Command.Group heading="Theme">
      <Command.Item onSelect={() => setMode('light')}>Light</Command.Item>
      <Command.Item onSelect={() => setMode('dark')}>Dark</Command.Item>
    </Command.Group>
  </Command.List>
</Command.Dialog>
```

Note: `cmdk-sv` is deprecated — Command is built into bits-ui.

## Select

```svelte
<Select.Root type="single">
  <Select.Trigger class="w-[180px]">
    <Select.Value placeholder="Select a fruit" />
  </Select.Trigger>
  <Select.Content>
    <Select.Group>
      <Select.GroupHeading>Fruits</Select.GroupHeading>
      <Select.Item value="apple">Apple</Select.Item>
      <Select.Item value="banana">Banana</Select.Item>
    </Select.Group>
  </Select.Content>
</Select.Root>
```

## Accordion

```svelte
<Accordion.Root type="single" collapsible>
  <Accordion.Item value="item-1">
    <Accordion.Trigger>Is it accessible?</Accordion.Trigger>
    <Accordion.Content>
      Yes — WAI-ARIA compliant.
    </Accordion.Content>
  </Accordion.Item>
</Accordion.Root>
```

## Toasts (svelte-sonner)

```svelte
<!-- +layout.svelte: add <Toaster /> -->
<script>
  import { Toaster } from "$lib/components/ui/sonner/index.js";
</script>
<Toaster />

<!-- Any component -->
<script>
  import { toast } from "svelte-sonner";
</script>

<button onclick={() => toast.success("Saved!")}>Save</button>
<button onclick={() => toast.error("Failed")}>Error</button>
<button onclick={() => toast.promise(saveData(), {
  loading: "Saving...",
  success: "Done!",
  error: "Failed",
})}>Async</button>
```

## Dropdown Menu

```svelte
<DropdownMenu.Root>
  <DropdownMenu.Trigger>
    {#snippet child({ props })}
      <Button {...props} variant="ghost" size="icon">
        <MoreHorizontal class="h-4 w-4" />
      </Button>
    {/snippet}
  </DropdownMenu.Trigger>
  <DropdownMenu.Content align="end">
    <DropdownMenu.Label>Actions</DropdownMenu.Label>
    <DropdownMenu.Separator />
    <DropdownMenu.Item onclick={() => edit(item)}>Edit</DropdownMenu.Item>
    <DropdownMenu.Item
      class="text-destructive"
      onclick={() => remove(item)}
    >
      Delete
    </DropdownMenu.Item>
  </DropdownMenu.Content>
</DropdownMenu.Root>
```

## Tooltip

```svelte
<Tooltip.Root>
  <Tooltip.Trigger>Hover me</Tooltip.Trigger>
  <Tooltip.Content>
    <p>Helpful information</p>
  </Tooltip.Content>
</Tooltip.Root>
```

Wrap the app in `<Tooltip.Provider>` to control global delay:

```svelte
<!-- +layout.svelte -->
<Tooltip.Provider delayDuration={200}>
  {@render children()}
</Tooltip.Provider>
```

## Card

```svelte
<Card.Root>
  <Card.Header>
    <Card.Title>Card Title</Card.Title>
    <Card.Description>Card description.</Card.Description>
  </Card.Header>
  <Card.Content>
    <p>Content</p>
  </Card.Content>
  <Card.Footer>
    <Button>Action</Button>
  </Card.Footer>
</Card.Root>
```

## Alert

```svelte
<Alert.Root variant="destructive">
  <AlertCircle class="h-4 w-4" />
  <Alert.Title>Error</Alert.Title>
  <Alert.Description>Something went wrong.</Alert.Description>
</Alert.Root>
```

## bits-ui Child Snippet Pattern

When shadcn-svelte's wrapper is too rigid, use the `child` snippet to render a custom element:

```svelte
<!-- Override the trigger element entirely -->
<Dialog.Trigger>
  {#snippet child({ props })}
    <a {...props} href="#" class="custom-link">Open Dialog</a>
  {/snippet}
</Dialog.Trigger>
```

For floating components (Popover, Tooltip, Select, Combobox, DropdownMenu), the child snippet receives both `props` and `wrapperProps`:

```svelte
<Popover.Content>
  {#snippet child({ wrapperProps, props })}
    <div {...wrapperProps}>
      <div {...props} class="my-custom-popover">Content</div>
    </div>
  {/snippet}
</Popover.Content>
```

Always spread both — `wrapperProps` handles positioning, `props` handles behavior and accessibility.
