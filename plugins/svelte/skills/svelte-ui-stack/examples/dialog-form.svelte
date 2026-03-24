<!-- Dialog with form — demonstrates architecture pattern:
     Logic in .svelte.ts, thin UI shell in .svelte -->
<script lang="ts">
  import * as Dialog from "$lib/components/ui/dialog/index.js";
  import * as Form from "$lib/components/ui/form/index.js";
  import { Input } from "$lib/components/ui/input/index.js";
  import { Button } from "$lib/components/ui/button/index.js";
  import { type SuperValidated, type Infer, superForm } from "sveltekit-superforms";
  import { zod4Client } from "sveltekit-superforms/adapters";
  import { memberSchema, type MemberSchema } from "./schema.js";

  let { data }: { data: { form: SuperValidated<Infer<MemberSchema>> } } = $props();
  let open = $state(false);

  const form = superForm(data.form, {
    validators: zod4Client(memberSchema),
    onResult: ({ result }) => {
      if (result.type === "success") open = false;
    },
  });
  const { form: formData, enhance } = form;
</script>

<Dialog.Root bind:open>
  <Dialog.Trigger>
    {#snippet child({ props })}
      <Button {...props}>Add Member</Button>
    {/snippet}
  </Dialog.Trigger>
  <Dialog.Content class="sm:max-w-[425px]">
    <Dialog.Header>
      <Dialog.Title>Add Team Member</Dialog.Title>
      <Dialog.Description>Invite a new member to the team.</Dialog.Description>
    </Dialog.Header>

    <form method="POST" use:enhance class="space-y-4">
      <Form.Field {form} name="name">
        <Form.Control>
          {#snippet children({ props })}
            <Form.Label>Name</Form.Label>
            <Input {...props} bind:value={$formData.name} />
          {/snippet}
        </Form.Control>
        <Form.FieldErrors />
      </Form.Field>

      <Form.Field {form} name="email">
        <Form.Control>
          {#snippet children({ props })}
            <Form.Label>Email</Form.Label>
            <Input {...props} type="email" bind:value={$formData.email} />
          {/snippet}
        </Form.Control>
        <Form.FieldErrors />
      </Form.Field>

      <Dialog.Footer>
        <Dialog.Close>
          {#snippet child({ props })}
            <Button {...props} variant="outline">Cancel</Button>
          {/snippet}
        </Dialog.Close>
        <Form.Button>Invite</Form.Button>
      </Dialog.Footer>
    </form>
  </Dialog.Content>
</Dialog.Root>
