<script lang="ts">
    let open = $state(false);
    let modalRef = $state<HTMLDivElement>();
    let previousFocus: HTMLElement | null = null;

    function openModal() {
        previousFocus = document.activeElement as HTMLElement;
        open = true;

        // Focus first focusable element after render
        setTimeout(() => {
            const firstFocusable = modalRef?.querySelector<HTMLElement>(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
            );
            firstFocusable?.focus();
        }, 0);
    }

    function closeModal() {
        open = false;
        previousFocus?.focus();
    }

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === "Escape") {
            closeModal();
            return;
        }

        if (e.key === "Tab" && modalRef) {
            const focusable = modalRef.querySelectorAll<HTMLElement>(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
            );

            if (!focusable.length) return;

            const first = focusable[0];
            const last = focusable[focusable.length - 1];

            if (e.shiftKey && document.activeElement === first) {
                e.preventDefault();
                last.focus();
            } else if (!e.shiftKey && document.activeElement === last) {
                e.preventDefault();
                first.focus();
            }
        }
    }
</script>

<button onclick={openModal}> Open Modal </button>

{#if open}
    <!-- Backdrop -->
    <div class="backdrop" onclick={closeModal} aria-hidden="true"></div>

    <!-- Modal -->
    <div
        bind:this={modalRef}
        class="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        aria-describedby="modal-description"
        onkeydown={handleKeydown}
        tabindex="-1"
    >
        <h2 id="modal-title">Modal Title</h2>
        <p id="modal-description">
            This is an accessible modal dialog with focus trap.
        </p>

        <div class="actions">
            <button onclick={closeModal}>Cancel</button>
            <button onclick={closeModal}>Confirm</button>
        </div>

        <button
            class="close-button"
            onclick={closeModal}
            aria-label="Close modal"
        >
            ×
        </button>
    </div>
{/if}

<style>
    .backdrop {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.5);
        z-index: 100;
    }

    .modal {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 2rem;
        border-radius: 8px;
        z-index: 101;
        max-width: 500px;
    }

    .close-button {
        position: absolute;
        top: 0.5rem;
        right: 0.5rem;
    }
</style>
