<script lang="ts">
    let email = $state("");
    let emailError = $state("");
    let emailTouched = $state(false);

    function validateEmail() {
        emailTouched = true;
        if (!email) {
            emailError = "Email is required";
        } else if (!email.includes("@")) {
            emailError = "Please enter a valid email address";
        } else {
            emailError = "";
        }
    }
</script>

<div class="form-group">
    <!-- Explicit label association (preferred) -->
    <label for="email">
        Email address
        <span class="required" aria-hidden="true">*</span>
        <span class="sr-only">(required)</span>
    </label>

    <input
        id="email"
        type="email"
        bind:value={email}
        onblur={validateEmail}
        aria-required="true"
        aria-invalid={emailTouched && emailError ? "true" : undefined}
        aria-describedby={emailError ? "email-error" : "email-hint"}
    />

    <!-- Hint text -->
    <p id="email-hint" class="hint">
        We'll never share your email with anyone.
    </p>

    <!-- Error message with live region -->
    {#if emailTouched && emailError}
        <p id="email-error" class="error" role="alert">
            {emailError}
        </p>
    {/if}
</div>

<style>
    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border: 0;
    }

    .required {
        color: #dc2626;
    }

    .hint {
        font-size: 0.875rem;
        color: #6b7280;
    }

    .error {
        font-size: 0.875rem;
        color: #dc2626;
    }

    input[aria-invalid="true"] {
        border-color: #dc2626;
    }
</style>
