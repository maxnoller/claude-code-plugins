<script lang="ts">
	import { enhance } from '$app/forms';

	let { data, form } = $props();
</script>

<svelte:head>
	<title>Blog Posts</title>
</svelte:head>

<main>
	<h1>Blog Posts</h1>

	<section>
		<h2>Create a new post</h2>

		{#if form?.error}
			<p class="error" role="alert">{form.error}</p>
		{/if}

		{#if form?.success}
			<p class="success" role="status">Post created successfully!</p>
		{/if}

		<form method="POST" action="?/create" use:enhance>
			<div>
				<label for="title">Title</label>
				<input
					id="title"
					name="title"
					type="text"
					required
					value={form?.title ?? ''}
				/>
			</div>

			<div>
				<label for="content">Content</label>
				<textarea
					id="content"
					name="content"
					required
					rows="4"
				>{form?.content ?? ''}</textarea>
			</div>

			<button type="submit">Create Post</button>
		</form>
	</section>

	<section>
		<h2>All Posts</h2>

		{#if data.posts.length === 0}
			<p>No posts yet. Create your first post above!</p>
		{:else}
			<ul class="posts">
				{#each data.posts as post (post.id)}
					<li class="post">
						<article>
							<h3>{post.title}</h3>
							<p>{post.content}</p>
							<time datetime={post.createdAt.toISOString?.() ?? post.createdAt}>
								{new Date(post.createdAt).toLocaleDateString()}
							</time>

							<form method="POST" action="?/delete" use:enhance>
								<input type="hidden" name="id" value={post.id} />
								<button type="submit">Delete</button>
							</form>
						</article>
					</li>
				{/each}
			</ul>
		{/if}
	</section>
</main>

<style>
	main {
		max-width: 48rem;
		margin: 0 auto;
		padding: 2rem;
	}

	.error {
		color: red;
	}

	.success {
		color: green;
	}

	.posts {
		list-style: none;
		padding: 0;
	}

	.post {
		border: 1px solid #ddd;
		border-radius: 0.5rem;
		padding: 1rem;
		margin-bottom: 1rem;
	}

	.post h3 {
		margin-top: 0;
	}

	form div {
		margin-bottom: 1rem;
	}

	label {
		display: block;
		font-weight: 600;
		margin-bottom: 0.25rem;
	}

	input,
	textarea {
		width: 100%;
		padding: 0.5rem;
		border: 1px solid #ccc;
		border-radius: 0.25rem;
	}

	button {
		padding: 0.5rem 1rem;
		border: none;
		border-radius: 0.25rem;
		cursor: pointer;
		background: #333;
		color: white;
	}

	button:hover {
		background: #555;
	}
</style>
