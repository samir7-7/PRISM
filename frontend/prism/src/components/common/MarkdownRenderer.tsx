import { useMemo } from 'react';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export const MarkdownRenderer = ({ content, className = '' }: MarkdownRendererProps) => {
  const formattedContent = useMemo(() => {
    let html = content;

    // Convert headers
    html = html.replace(/^### (.*$)/gim, '<h3 class="text-h4 text-prism-text font-semibold mt-6 mb-3">$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2 class="text-h3 text-prism-text font-semibold mt-6 mb-3">$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1 class="text-h2 text-prism-text font-bold mt-6 mb-4">$1</h1>');

    // Convert bold text
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-prism-text">$1</strong>');
    html = html.replace(/__(.*?)__/g, '<strong class="font-semibold text-prism-text">$1</strong>');

    // Convert italic text
    html = html.replace(/\*(.*?)\*/g, '<em class="italic">$1</em>');
    html = html.replace(/_(.*?)_/g, '<em class="italic">$1</em>');

    // Convert inline code
    html = html.replace(/`([^`]+)`/g, '<code class="code-inline">$1</code>');

    // Convert code blocks
    html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
      return `<pre class="code-block my-4"><code class="text-code">${escapeHtml(code.trim())}</code></pre>`;
    });

    // Convert unordered lists
    html = html.replace(/^\* (.*$)/gim, '<li class="ml-4 mb-2">• $1</li>');
    html = html.replace(/^- (.*$)/gim, '<li class="ml-4 mb-2">• $1</li>');
    html = html.replace(/(<li.*<\/li>)/s, '<ul class="my-3 space-y-1">$1</ul>');

    // Convert ordered lists
    html = html.replace(/^\d+\. (.*$)/gim, '<li class="ml-4 mb-2">$1</li>');
    html = html.replace(/(<li.*<\/li>)/s, '<ol class="my-3 space-y-1 list-decimal list-inside">$1</ol>');

    // Convert links
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="text-prism-blue hover:text-prism-blue/80 underline transition-colors" target="_blank" rel="noopener noreferrer">$1</a>');

    // Convert blockquotes
    html = html.replace(/^> (.*$)/gim, '<blockquote class="border-l-4 border-prism-blue pl-4 py-2 my-3 text-prism-text-muted italic">$1</blockquote>');

    // Convert horizontal rules
    html = html.replace(/^---$/gim, '<hr class="divider my-6" />');
    html = html.replace(/^\*\*\*$/gim, '<hr class="divider my-6" />');

    // Convert line breaks
    html = html.replace(/\n\n/g, '</p><p class="mb-3">');
    html = html.replace(/\n/g, '<br />');

    // Wrap in paragraph if not already wrapped
    if (!html.startsWith('<')) {
      html = `<p class="mb-3">${html}</p>`;
    }

    return html;
  }, [content]);

  const escapeHtml = (text: string) => {
    const map: { [key: string]: string } = {
      '&': '&',
      '<': '<',
      '>': '>',
      '"': '"',
      "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, (m) => map[m]);
  };

  return (
    <div
      className={`markdown-content text-body-sm text-prism-text-muted leading-relaxed ${className}`}
      dangerouslySetInnerHTML={{ __html: formattedContent }}
    />
  );
};

// Made with Bob