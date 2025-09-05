<script lang="ts">
	import { createEventDispatcher } from "svelte";
	import { copy, css_units } from "@gradio/utils";
	import type { CopyData } from "@gradio/utils";
	import { Copy, Check } from "@gradio/icons";
	import type { LoadingStatus } from "@gradio/statustracker";
	import { IconButton, IconButtonWrapper } from "@gradio/atoms";
	import type { ThemeMode } from "@gradio/core";

	import { MarkdownCode } from "@gradio/markdown-code";

	export let elem_classes: string[] = [];
	export let visible = true;
	export let value: string;
	export let tooltip: string | null = null;
	export let min_height: number | string | undefined = undefined;
	export let rtl = false;
	export let sanitize_html = true;
	export let line_breaks = false;
	export let latex_delimiters: {
		left: string;
		right: string;
		display: boolean;
	}[];
	export let header_links = false;
	export let height: number | string | undefined = undefined;
	export let show_copy_button = false;
	export let loading_status: LoadingStatus | undefined = undefined;
	export let theme_mode: ThemeMode;
	let copied = false;
	let timer: NodeJS.Timeout;

	const dispatch = createEventDispatcher<{
		change: undefined;
		copy: CopyData;
	}>();

	$: value, dispatch("change");

	async function handle_copy(): Promise<void> {
		if ("clipboard" in navigator) {
			await navigator.clipboard.writeText(value);
			dispatch("copy", { value: value });
			copy_feedback();
		}
	}

	function copy_feedback(): void {
		copied = true;
		if (timer) clearTimeout(timer);
		timer = setTimeout(() => {
			copied = false;
		}, 1000);
	}

	function showTooltip(event: MouseEvent): void {
		const target = event.target as HTMLElement;
		const tooltipText = target.nextElementSibling as HTMLElement;
		if (tooltipText) {
			const rect = target.getBoundingClientRect();
			const tooltipRect = tooltipText.getBoundingClientRect();
			
			// Position above the icon
			let top = rect.top - tooltipRect.height - 10;
			let left = rect.left + rect.width / 2 - tooltipRect.width / 2;
			
			// Adjust if tooltip goes off screen
			if (left < 10) left = 10;
			if (left + tooltipRect.width > window.innerWidth - 10) {
				left = window.innerWidth - tooltipRect.width - 10;
			}
			if (top < 10) {
				top = rect.bottom + 10;
			}
			
			tooltipText.style.top = `${top}px`;
			tooltipText.style.left = `${left}px`;
		}
	}
</script>

<div
	class="prose {elem_classes?.join(' ') || ''}"
	class:hide={!visible}
	data-testid="markdown"
	dir={rtl ? "rtl" : "ltr"}
	use:copy
	style={height ? `max-height: ${css_units(height)}; overflow-y: auto;` : ""}
	style:min-height={min_height && loading_status?.status !== "pending"
		? css_units(min_height)
		: undefined}
>
	{#if show_copy_button}
		<IconButtonWrapper>
			<IconButton
				Icon={copied ? Check : Copy}
				on:click={handle_copy}
				label={copied ? "Copied conversation" : "Copy conversation"}
			></IconButton>
		</IconButtonWrapper>
	{/if}
	<span class="markdown-wrapper">
		<MarkdownCode
			message={value}
			{latex_delimiters}
			{sanitize_html}
			{line_breaks}
			chatbot={false}
			{header_links}
			{theme_mode}
		/>
		{#if tooltip}
			<span class="tooltip-container">
				<span class="tooltip-icon">?</span>
				<span class="tooltip-text">{tooltip}</span>
			</span>
		{/if}
	</span>
</div>

<style>
	div :global(.math.inline) {
		fill: var(--body-text-color);
		display: inline-block;
		vertical-align: middle;
		padding: var(--size-1-5) -var(--size-1);
		color: var(--body-text-color);
	}

	div :global(.math.inline svg) {
		display: inline;
		margin-bottom: 0.22em;
	}

	div {
		max-width: 100%;
	}

	.hide {
		display: none;
	}

	.markdown-wrapper {
		display: inline-block;
		width: 100%;
	}

	.markdown-wrapper :global(div),
	.markdown-wrapper :global(p),
	.markdown-wrapper :global(h1),
	.markdown-wrapper :global(h2),
	.markdown-wrapper :global(h3),
	.markdown-wrapper :global(h4),
	.markdown-wrapper :global(h5),
	.markdown-wrapper :global(h6) {
		display: inline;
	}

	.tooltip-container {
		position: relative;
		display: inline;
		margin-left: 4px;
	}

	.tooltip-icon {
		display: inline-block;
		width: 16px;
		height: 16px;
		border-radius: 50%;
		background-color: var(--color-accent);
		color: white;
		font-size: 11px;
		font-weight: bold;
		text-align: center;
		line-height: 16px;
		cursor: help;
		transition: all 0.2s ease;
		vertical-align: middle;
		margin-top: -5px;
	}

	.tooltip-icon:hover {
		background-color: var(--color-accent-soft);
		transform: scale(1.1);
	}

	.tooltip-text {
		visibility: hidden;
		opacity: 0;
		position: fixed;
		bottom: auto;
		top: auto;
		left: auto;
		right: auto;
		transform: none;
		background-color: rgba(0, 0, 0, 0.9);
		color: white;
		padding: 12px 16px;
		border-radius: 6px;
		font-size: 12px;
		z-index: 10000;
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
		transition: opacity 0.3s ease, visibility 0.3s ease;
		max-width: 300px;
		min-width: 150px;
		white-space: normal;
		line-height: 1.4;
		pointer-events: none;
		word-wrap: break-word;
		text-align: left;
		overflow: visible;
	}

	.tooltip-text::after {
		content: "";
		position: absolute;
		top: 100%;
		left: 50%;
		margin-left: -5px;
		border-width: 5px;
		border-style: solid;
		border-color: rgba(0, 0, 0, 0.9) transparent transparent transparent;
	}

	.tooltip-container:hover .tooltip-text {
		visibility: visible;
		opacity: 1;
	}
</style>
