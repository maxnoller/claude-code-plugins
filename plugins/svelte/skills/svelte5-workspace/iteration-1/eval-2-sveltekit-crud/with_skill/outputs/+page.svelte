<script lang="ts">
	import { enhance } from '$app/forms';

	let { data, form } = $props();
	let creating = $state(false);
	let deletingId = $state<string | null>(null);
</script>

<svelte:head>
	<title>Blog Posts</title>
</svelte:head>

<main>
	<h1>Blog Posts</h1>

	<!-- Create post form with progressive enhancement -->
	<section aria-labelledby="create-heading">
		<h2 id="create-heading">Create New Post</h2>

		{#if form?.error}
			<p role="alert" class="error">{form.error}</p>
		{/if}

		{#if form?.success}
			<p role="status" class="success">Post created successfully!</p>
		{/if}

		<form
			method="POST"
			action="?/create"
			use:enhance={() => {
				creating = true;
				return async ({ update }) => {
					await update();
					creating = false;
				};
			}}
		>
			<div>
				<label for="title">Title</label>
				<input
					id="title"
					name="title"
					type="text"
					required
					value={form?.title ?? ''}
					aria-invalid={form?.error && !form?.title?.trim() ? 'true' : undefined}
				/>
			</div>

			<div>
				<label for="content">Content</label>
				<textarea
					id="content"
					name="content"
					required
					rows="4"
					aria-invalid={form?.error && !form?.content?.trim() ? 'true' : undefined}
				>{form?.content ?? ''}</textarea>
			</div>

			<button type="submit" disabled={creating}>
				{creating ? 'Creating...' : 'Create Post'}
			</button>
		</form>
	</section>

	<!-- Post list -->
	<section aria-labelledby="posts-heading">
		<h2 id="posts-heading">All Posts</h2>

		{#if data.posts.length === 0}
			<p>No posts yet. Create your first one above!</p>
		{:else}
			<ul role="list">
				{#each data.posts as post (post.id)}
					<li>
						<article>
							<h3>{post.title}</h3>
							<p>{post.content}</p>
							<time datetime={post.createdAt}>
								{new Date(post.createdAt).toLocaleDateString()}
							</time>

							<form
								method="POST"
								action="?/delete"
								use:enhance={() => {
									deletingId = post.id;
									return async ({ update }) => {
										await update();
										deletingId = null;
									};
								}}
							>
								<input type="hidden" name="id" value={post.id} />
								<button type="submit" disabled={deletingId === post.id} aria-label="Delete {post.title}">
									{deletingId === post.id ? 'Deleting...' : 'Delete'}
								</button>
							</form>
						</article>
					</li>
				{/each}
			</ul>
		{/if}
	</section>
</main>
