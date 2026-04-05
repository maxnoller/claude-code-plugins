<script lang="ts">
    import { onMount } from "svelte";

    let count = $state(0);
    let windowWidth = $state(0);
    let data = $state<string[]>([]);

    // CORRECT: Effect with cleanup for interval
    $effect(() => {
        const id = setInterval(() => {
            count++;
        }, 1000);

        return () => clearInterval(id);
    });

    // CORRECT: Effect with cleanup for event listener
    $effect(() => {
        function handleResize() {
            windowWidth = window.innerWidth;
        }

        window.addEventListener("resize", handleResize);
        handleResize(); // Initial value

        return () => window.removeEventListener("resize", handleResize);
    });

    // CORRECT: Effect with cleanup for fetch abort
    $effect(() => {
        const controller = new AbortController();

        fetch("/api/data", { signal: controller.signal })
            .then((r) => r.json())
            .then((d) => (data = d))
            .catch((e) => {
                if (e.name !== "AbortError") {
                    console.error("Fetch failed:", e);
                }
            });

        return () => controller.abort();
    });
</script>

<div>
    <p>Count: {count}</p>
    <p>Window width: {windowWidth}px</p>
    <p>Data items: {data.length}</p>
</div>
