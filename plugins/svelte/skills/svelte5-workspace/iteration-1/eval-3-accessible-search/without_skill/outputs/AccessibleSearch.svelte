<script lang="ts">
	import { search, type SearchResult } from './search.remote';

	let searchTerm = $state('');
	let results = $state<SearchResult[]>([]);
	let loading = $state(false);
	let activeIndex = $state(-1);
	let announcement = $state('');
	let listboxOpen = $state(false);
	let debounceTimer: ReturnType<typeof setTimeout> | undefined;
	let inputEl: HTMLInputElement | undefined;

	const listboxId = 'search-listbox';

	function debounce(fn: () => void, ms: number) {
		clearTimeout(debounceTimer);
		debounceTimer = setTimeout(fn, ms);
	}

	async function performSearch(term: string) {
		if (!term.trim()) {
			results = [];
			listboxOpen = false;
			announcement = '';
			loading = false;
			return;
		}

		loading = true;
		announcement = 'Searching...';

		try {
			results = await search(term);
			listboxOpen = results.length > 0;
			activeIndex = -1;

			if (results.length === 0) {
				announcement = `No results found for "${term}".`;
			} else if (results.length === 1) {
				announcement = `1 result found for "${term}".`;
			} else {
				announcement = `${results.length} results found for "${term}".`;
			}
		} catch {
			results = [];
			listboxOpen = false;
			announcement = 'Search failed. Please try again.';
		} finally {
			loading = false;
		}
	}

	function handleInput() {
		debounce(() => performSearch(searchTerm), 300);
	}

	function handleKeydown(event: KeyboardEvent) {
		if (!listboxOpen) return;

		switch (event.key) {
			case 'ArrowDown': {
				event.preventDefault();
				activeIndex = activeIndex < results.length - 1 ? activeIndex + 1 : 0;
				break;
			}
			case 'ArrowUp': {
				event.preventDefault();
				activeIndex = activeIndex > 0 ? activeIndex - 1 : results.length - 1;
				break;
			}
			case 'Enter': {
				event.preventDefault();
				if (activeIndex >= 0 && activeIndex < results.length) {
					selectResult(results[activeIndex]);
				}
				break;
			}
			case 'Escape': {
				event.preventDefault();
				listboxOpen = false;
				activeIndex = -1;
				inputEl?.focus();
				break;
			}
			case 'Home': {
				if (listboxOpen && results.length > 0) {
					event.preventDefault();
					activeIndex = 0;
				}
				break;
			}
			case 'End': {
				if (listboxOpen && results.length > 0) {
					event.preventDefault();
					activeIndex = results.length - 1;
				}
				break;
			}
		}
	}

	function selectResult(result: SearchResult) {
		searchTerm = result.title;
		listboxOpen = false;
		activeIndex = -1;
		announcement = `Selected: ${result.title}`;
		// Navigate or handle selection
		window.location.href = result.url;
	}

	function handleBlur(event: FocusEvent) {
		const relatedTarget = event.relatedTarget as HTMLElement | null;
		if (!relatedTarget?.closest('[role="listbox"]')) {
			// Delay closing so click on result can register
			setTimeout(() => {
				listboxOpen = false;
				activeIndex = -1;
			}, 150);
		}
	}

	let activeDescendantId = $derived(
		activeIndex >= 0 ? `search-option-${results[activeIndex]?.id}` : undefined
	);
</script>

<div class="search-wrapper">
	<label for="search-input" class="search-label">Search</label>

	<div class="search-input-wrapper">
		<input
			bind:this={inputEl}
			bind:value={searchTerm}
			oninput={handleInput}
			onkeydown={handleKeydown}
			onblur={handleBlur}
			id="search-input"
			type="search"
			role="combobox"
			aria-expanded={listboxOpen}
			aria-controls={listboxId}
			aria-activedescendant={activeDescendantId}
			aria-autocomplete="list"
			aria-busy={loading}
			aria-describedby="search-help"
			autocomplete="off"
			placeholder="Search..."
		/>
		{#if loading}
			<span class="loading-indicator" aria-hidden="true"></span>
		{/if}
	</div>

	<span id="search-help" class="visually-hidden">
		Type to search. Use arrow keys to navigate results, Enter to select, Escape to close.
	</span>

	{#if listboxOpen}
		<ul
			id={listboxId}
			role="listbox"
			aria-label="Search results"
		>
			{#each results as result, i (result.id)}
				{@const isActive = i === activeIndex}
				<li
					id="search-option-{result.id}"
					role="option"
					aria-selected={isActive}
					class:active={isActive}
					onmouseenter={() => (activeIndex = i)}
					onclick={() => selectResult(result)}
				>
					<span class="result-title">{result.title}</span>
					<span class="result-description">{result.description}</span>
				</li>
			{/each}
		</ul>
	{/if}

	<!-- Live region for screen reader announcements -->
	<div
		aria-live="polite"
		aria-atomic="true"
		class="visually-hidden"
		role="status"
	>
		{announcement}
	</div>
</div>

<style>
	.search-wrapper {
		position: relative;
		max-width: 32rem;
		width: 100%;
	}

	.search-label {
		display: block;
		font-weight: 600;
		margin-block-end: 0.25rem;
		font-size: 0.875rem;
	}

	.search-input-wrapper {
		position: relative;
		display: flex;
		align-items: center;
	}

	input[type='search'] {
		width: 100%;
		padding: 0.5rem 0.75rem;
		padding-inline-end: 2rem;
		border: 1px solid #d1d5db;
		border-radius: 0.375rem;
		font-size: 1rem;
		line-height: 1.5;
		outline: none;
		transition: border-color 0.15s;
	}

	input[type='search']:focus {
		border-color: #2563eb;
		box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.25);
	}

	.loading-indicator {
		position: absolute;
		inset-inline-end: 0.5rem;
		width: 1rem;
		height: 1rem;
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

	ul[role='listbox'] {
		position: absolute;
		z-index: 10;
		width: 100%;
		margin-block-start: 0.25rem;
		padding: 0.25rem 0;
		list-style: none;
		background: white;
		border: 1px solid #d1d5db;
		border-radius: 0.375rem;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
		max-height: 20rem;
		overflow-y: auto;
	}

	li[role='option'] {
		display: flex;
		flex-direction: column;
		gap: 0.125rem;
		padding: 0.5rem 0.75rem;
		cursor: pointer;
	}

	li[role='option']:hover,
	li[role='option'].active {
		background: #eff6ff;
	}

	li[role='option'].active {
		outline: 2px solid #2563eb;
		outline-offset: -2px;
	}

	.result-title {
		font-weight: 500;
		color: #111827;
	}

	.result-description {
		font-size: 0.875rem;
		color: #6b7280;
	}

	.visually-hidden {
		position: absolute;
		width: 1px;
		height: 1px;
		padding: 0;
		margin: -1px;
		overflow: hidden;
		clip: rect(0, 0, 0, 0);
		white-space: nowrap;
		border-width: 0;
	}
</style>
