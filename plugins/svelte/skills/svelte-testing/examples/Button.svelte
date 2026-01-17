<script lang="ts">
    interface Props {
        label?: string;
        disabled?: boolean;
        loading?: boolean;
        type?: "button" | "submit" | "reset";
        onclick?: (e: MouseEvent) => void;
    }

    let {
        label = "Button",
        disabled = false,
        loading = false,
        type = "button",
        onclick,
    }: Props = $props();
</script>

<button
    {type}
    disabled={disabled || loading}
    aria-busy={loading}
    {onclick}
    class="btn"
>
    {#if loading}
        <span class="loader">Loading...</span>
    {/if}
    {label}
</button>

<style>
    .btn {
        padding: 0.5rem 1rem;
        border-radius: 4px;
    }
</style>
