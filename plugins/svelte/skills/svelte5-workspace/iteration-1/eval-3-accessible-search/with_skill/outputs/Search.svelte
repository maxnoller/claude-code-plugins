<script lang="ts">
	import { search, type SearchResult } from './search.remote';

	let inputValue = $state('');
	let results = $state<SearchResult[]>([]);
	let loading = $state(false);
	let activeIndex = $state(-1);
	let open = $state(false);
	let announcement = $state('');
	let inputRef = $state<HTMLInputElement>();
	let listRef = $state<HTMLUListElement>();

	// Debounced search via $effect with cleanup
	$effect(() => {
		const term = inputValue;

		if (term.trim().length < 2) {
			results = [];
			open = false;
			announcement = '';
			return;
		}

		loading = true;
		const timeout = setTimeout(async () => {
			try {
				results = await search(term);
				open = results.length > 0;
				activeIndex = -1;

				if (results.length === 0) {
					announcement = `No results found for "${term}".`;
				} else {
					announcement = `${results.length} result${results.length === 1 ? '' : 's'} found. Use arrow keys to navigate.`;
				}
			} catch {
				results = [];
				open = false;
				announcement = 'Search failed. Please try again.';
			} finally {
				loading = false;
			}
		}, 300);

		return () => {
			clearTimeout(timeout);
		};
	});

	function handleKeydown(e: KeyboardEvent) {
		if (!open && results.length === 0) return;

		switch (e.key) {
			case 'ArrowDown':
				e.preventDefault();
				if (!open && results.length > 0) {
					open = true;
					activeIndex = 0;
				} else {
					activeIndex = (activeIndex + 1) % results.length;
				}
				scrollActiveIntoView();
				break;

			case 'ArrowUp':
				e.preventDefault();
				if (activeIndex <= 0) {
					activeIndex = results.length - 1;
				} else {
					activeIndex--;
				}
				scrollActiveIntoView();
				break;

			case 'Home':
				if (open) {
					e.preventDefault();
					activeIndex = 0;
					scrollActiveIntoView();
				}
				break;

			case 'End':
				if (open) {
					e.preventDefault();
					activeIndex = results.length - 1;
					scrollActiveIntoView();
				}
				break;

			case 'Enter':
				if (activeIndex >= 0 && results[activeIndex]) {
					e.preventDefault();
					selectResult(results[activeIndex]);
				}
				break;

			case 'Escape':
				e.preventDefault();
				close();
				break;
		}
	}

	function scrollActiveIntoView() {
		// Wait for DOM update, then scroll
		requestAnimationFrame(() => {
			const active = listRef?.querySelector('[aria-selected="true"]');
			active?.scrollIntoView({ block: 'nearest' });
		});
	}

	function selectResult(result: SearchResult) {
		inputValue = result.title;
		close();
		announcement = `Selected: ${result.title}`;
		window.location.href = result.url;
	}

	function close() {
		open = false;
		activeIndex = -1;
		inputRef?.focus();
	}

	function handleBlur(e: FocusEvent) {
		// Close the listbox when focus leaves the search component entirely
		const related = e.relatedTarget as HTMLElement | null;
		if (related && listRef?.contains(related)) return;
		// Small delay so click on result registers before close
		setTimeout(() => {
			open = false;
			activeIndex = -1;
		}, 150);
	}
</script>

<div class="search-container">
	<label for="search-input" class="sr-only">Search</label>
	<div class="search-input-wrapper">
		<input
			bind:this={inputRef}
			id="search-input"
			type="search"
			role="combobox"
			autocomplete="off"
			aria-expanded={open}
			aria-controls="search-listbox"
			aria-activedescendant={activeIndex >= 0 ? `search-result-${activeIndex}` : undefined}
			aria-autocomplete="list"
			aria-busy={loading}
			placeholder="Search..."
			bind:value={inputValue}
			onkeydown={handleKeydown}
			onblur={handleBlur}
		/>
		{#if loading}
			<span class="search-spinner" aria-hidden="true"></span>
		{/if}
	</div>

	<ul
		bind:this={listRef}
		id="search-listbox"
		role="listbox"
		aria-label="Search results"
		hidden={!open}
	>
		{#each results as result, i (result.id)}
			<li
				id="search-result-{i}"
				role="option"
				aria-selected={activeIndex === i}
				onclick={() => selectResult(result)}
				onmouseenter={() => (activeIndex = i)}
			>
				<span class="result-title">{result.title}</span>
				<span class="result-description">{result.description}</span>
			</li>
		{/each}
	</ul>

	<!-- Live region for screen reader announcements -->
	<div aria-live="polite" aria-atomic="true" class="sr-only">
		{announcement}
	</div>
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

	.search-container {
		position: relative;
		width: 100%;
		max-width: 32rem;
	}

	.search-input-wrapper {
		position: relative;
		display: flex;
		align-items: center;
	}

	input[type='search'] {
		width: 100%;
		padding: 0.625rem 2.5rem 0.625rem 0.75rem;
		font-size: 1rem;
		line-height: 1.5;
		border: 2px solid #6b7280;
		border-radius: 0.5rem;
		background: #fff;
		color: #111827;
		outline: none;
	}

	input[type='search']:focus {
		border-color: #2563eb;
		box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.25);
	}

	.search-spinner {
		position: absolute;
		right: 0.75rem;
		width: 1.25rem;
		height: 1.25rem;
		border: 2px solid #d1d5db;
		border-top-color: #2563eb;
		border-radius: 50%;
		animation: spin 0.6s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	ul {
		position: absolute;
		top: 100%;
		left: 0;
		right: 0;
		margin: 0.25rem 0 0;
		padding: 0.25rem 0;
		list-style: none;
		background: #fff;
		border: 2px solid #d1d5db;
		border-radius: 0.5rem;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
		max-height: 20rem;
		overflow-y: auto;
		z-index: 50;
	}

	li {
		display: flex;
		flex-direction: column;
		gap: 0.125rem;
		padding: 0.5rem 0.75rem;
		cursor: pointer;
	}

	li[aria-selected='true'] {
		background: #eff6ff;
		outline: 2px solid #2563eb;
		outline-offset: -2px;
	}

	.result-title {
		font-weight: 600;
		color: #111827;
	}

	.result-description {
		font-size: 0.875rem;
		color: #6b7280;
	}

	@media (prefers-reduced-motion: reduce) {
		.search-spinner {
			animation-duration: 0.01ms !important;
			animation-iteration-count: 1 !important;
		}
	}
</style>
