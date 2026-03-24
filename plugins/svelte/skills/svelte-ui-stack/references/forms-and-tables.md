# Forms & Data Tables

## Forms: Formsnap + Superforms

### Installation

```bash
pnpm dlx shadcn-svelte@latest add form input button select checkbox textarea
pnpm add sveltekit-superforms formsnap
```

### Schema

```ts
// src/routes/settings/schema.ts
import { z } from "zod";

export const profileSchema = z.object({
  username: z.string().min(2, "At least 2 characters").max(50),
  email: z.string().email("Invalid email"),
  role: z.enum(["admin", "user", "viewer"]),
  bio: z.string().max(160).optional(),
  terms: z.boolean().refine(v => v, "Must accept terms"),
});

export type ProfileSchema = typeof profileSchema;
```

### Server

```ts
// src/routes/settings/+page.server.ts
import type { Actions, PageServerLoad } from "./$types";
import { fail } from "@sveltejs/kit";
import { superValidate } from "sveltekit-superforms";
import { zod4 } from "sveltekit-superforms/adapters";
import { profileSchema } from "./schema";

export const load: PageServerLoad = async () => {
  return { form: await superValidate(zod4(profileSchema)) };
};

export const actions: Actions = {
  default: async (event) => {
    const form = await superValidate(event, zod4(profileSchema));
    if (!form.valid) return fail(400, { form });
    await updateProfile(form.data);
    return { form };
  },
};
```

### Form Component

```svelte
<script lang="ts">
  import * as Form from "$lib/components/ui/form/index.js";
  import { Input } from "$lib/components/ui/input/index.js";
  import { Textarea } from "$lib/components/ui/textarea/index.js";
  import * as Select from "$lib/components/ui/select/index.js";
  import { Checkbox } from "$lib/components/ui/checkbox/index.js";
  import { profileSchema, type ProfileSchema } from "./schema.js";
  import {
    type SuperValidated,
    type Infer,
    superForm,
  } from "sveltekit-superforms";
  import { zod4Client } from "sveltekit-superforms/adapters";

  let { data }: { data: { form: SuperValidated<Infer<ProfileSchema>> } } = $props();

  const form = superForm(data.form, {
    validators: zod4Client(profileSchema),
  });
  const { form: formData, enhance } = form;
</script>

<form method="POST" use:enhance class="space-y-6">
  <!-- Text Input -->
  <Form.Field {form} name="username">
    <Form.Control>
      {#snippet children({ props })}
        <Form.Label>Username</Form.Label>
        <Input {...props} bind:value={$formData.username} />
      {/snippet}
    </Form.Control>
    <Form.Description>Your public display name.</Form.Description>
    <Form.FieldErrors />
  </Form.Field>

  <!-- Email -->
  <Form.Field {form} name="email">
    <Form.Control>
      {#snippet children({ props })}
        <Form.Label>Email</Form.Label>
        <Input {...props} type="email" bind:value={$formData.email} />
      {/snippet}
    </Form.Control>
    <Form.FieldErrors />
  </Form.Field>

  <!-- Select -->
  <Form.Field {form} name="role">
    <Form.Control>
      {#snippet children({ props })}
        <Form.Label>Role</Form.Label>
        <Select.Root type="single" bind:value={$formData.role}>
          <Select.Trigger {...props}>
            <Select.Value placeholder="Select role" />
          </Select.Trigger>
          <Select.Content>
            <Select.Item value="admin">Admin</Select.Item>
            <Select.Item value="user">User</Select.Item>
            <Select.Item value="viewer">Viewer</Select.Item>
          </Select.Content>
        </Select.Root>
      {/snippet}
    </Form.Control>
    <Form.FieldErrors />
  </Form.Field>

  <!-- Textarea -->
  <Form.Field {form} name="bio">
    <Form.Control>
      {#snippet children({ props })}
        <Form.Label>Bio</Form.Label>
        <Textarea {...props} bind:value={$formData.bio} />
      {/snippet}
    </Form.Control>
    <Form.Description>Max 160 characters.</Form.Description>
    <Form.FieldErrors />
  </Form.Field>

  <!-- Checkbox -->
  <Form.Field {form} name="terms">
    <Form.Control>
      {#snippet children({ props })}
        <div class="flex items-center gap-2">
          <Checkbox {...props} bind:checked={$formData.terms} />
          <Form.Label>Accept terms and conditions</Form.Label>
        </div>
      {/snippet}
    </Form.Control>
    <Form.FieldErrors />
  </Form.Field>

  <Form.Button>Save</Form.Button>
</form>
```

### Key Points

- Use `zod4` / `zod4Client` adapters (current superforms versions)
- `Form.Control` uses a `children` snippet receiving `{ props }` — spread on the input
- Bind form store values: `bind:value={$formData.fieldName}`
- `Form.FieldErrors` auto-displays errors for the parent `Form.Field`
- `use:enhance` enables AJAX submission with progressive enhancement

---

## Data Tables: TanStack Table

### Installation

```bash
pnpm dlx shadcn-svelte@latest add table
pnpm add @tanstack/table-core
```

shadcn-svelte provides `createSvelteTable`, `FlexRender`, `renderComponent`, and `renderSnippet` utilities.

### Column Definitions

```ts
// columns.ts
import type { ColumnDef } from "@tanstack/table-core";
import {
  renderComponent,
  renderSnippet,
} from "$lib/components/ui/data-table/index.js";
import SortButton from "./sort-button.svelte";
import ActionsCell from "./actions-cell.svelte";

export type Payment = {
  id: string;
  amount: number;
  status: "pending" | "processing" | "success" | "failed";
  email: string;
};

export const columns: ColumnDef<Payment>[] = [
  {
    accessorKey: "status",
    header: "Status",
  },
  {
    accessorKey: "email",
    header: ({ column }) =>
      renderComponent(SortButton, {
        label: "Email",
        onclick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      }),
  },
  {
    accessorKey: "amount",
    header: "Amount",
    cell: ({ row }) => {
      const formatted = new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
      }).format(parseFloat(row.getValue("amount")));
      return formatted;
    },
  },
  {
    id: "actions",
    cell: ({ row }) =>
      renderComponent(ActionsCell, { payment: row.original }),
  },
];
```

### Table Component

```svelte
<script lang="ts">
  import {
    createSvelteTable,
    FlexRender,
  } from "$lib/components/ui/data-table/index.js";
  import * as Table from "$lib/components/ui/table/index.js";
  import {
    getCoreRowModel,
    getSortedRowModel,
    getFilteredRowModel,
    getPaginationRowModel,
    type SortingState,
  } from "@tanstack/table-core";
  import { columns, type Payment } from "./columns.js";
  import { Input } from "$lib/components/ui/input/index.js";
  import { Button } from "$lib/components/ui/button/index.js";

  let { data }: { data: Payment[] } = $props();
  let sorting = $state<SortingState>([]);
  let globalFilter = $state("");

  const table = createSvelteTable({
    get data() { return data; },
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onSortingChange: (updater) => {
      sorting = typeof updater === "function" ? updater(sorting) : updater;
    },
    onGlobalFilterChange: (updater) => {
      globalFilter = typeof updater === "function" ? updater(globalFilter) : updater;
    },
    state: {
      get sorting() { return sorting; },
      get globalFilter() { return globalFilter; },
    },
  });
</script>

<!-- Filter -->
<Input
  placeholder="Filter..."
  value={globalFilter}
  oninput={(e) => globalFilter = e.currentTarget.value}
  class="max-w-sm"
/>

<!-- Table -->
<div class="rounded-md border">
  <Table.Root>
    <Table.Header>
      {#each table.getHeaderGroups() as headerGroup}
        <Table.Row>
          {#each headerGroup.headers as header}
            <Table.Head>
              {#if !header.isPlaceholder}
                <FlexRender
                  content={header.column.columnDef.header}
                  context={header.getContext()}
                />
              {/if}
            </Table.Head>
          {/each}
        </Table.Row>
      {/each}
    </Table.Header>
    <Table.Body>
      {#each table.getRowModel().rows as row}
        <Table.Row>
          {#each row.getVisibleCells() as cell}
            <Table.Cell>
              <FlexRender
                content={cell.column.columnDef.cell}
                context={cell.getContext()}
              />
            </Table.Cell>
          {/each}
        </Table.Row>
      {:else}
        <Table.Row>
          <Table.Cell colspan={columns.length} class="h-24 text-center">
            No results.
          </Table.Cell>
        </Table.Row>
      {/each}
    </Table.Body>
  </Table.Root>
</div>

<!-- Pagination -->
<div class="flex items-center justify-end gap-2 py-4">
  <Button
    variant="outline"
    size="sm"
    onclick={() => table.previousPage()}
    disabled={!table.getCanPreviousPage()}
  >
    Previous
  </Button>
  <Button
    variant="outline"
    size="sm"
    onclick={() => table.nextPage()}
    disabled={!table.getCanNextPage()}
  >
    Next
  </Button>
</div>
```

### Key Points

- Use `createSvelteTable` (not `useTable` or `createTable`)
- Use getter functions for reactive state: `get data() { return data; }`
- `renderComponent` for Svelte components in cells/headers
- `renderSnippet` for snippet-based cell rendering
- State handlers use updater functions for TanStack's state management pattern
