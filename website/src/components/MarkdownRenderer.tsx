import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useEffect } from "react";
import hljs from "highlight.js/lib/core";
import typescript from "highlight.js/lib/languages/typescript";
import javascript from "highlight.js/lib/languages/javascript";
import python from "highlight.js/lib/languages/python";
import bash from "highlight.js/lib/languages/bash";
import json from "highlight.js/lib/languages/json";
import css from "highlight.js/lib/languages/css";
import xml from "highlight.js/lib/languages/xml";
import "highlight.js/styles/github-dark.css";

// Register languages
hljs.registerLanguage("typescript", typescript);
hljs.registerLanguage("javascript", javascript);
hljs.registerLanguage("python", python);
hljs.registerLanguage("bash", bash);
hljs.registerLanguage("shell", bash);
hljs.registerLanguage("json", json);
hljs.registerLanguage("css", css);
hljs.registerLanguage("html", xml);
hljs.registerLanguage("xml", xml);

interface MarkdownRendererProps {
  content: string;
}

export default function MarkdownRenderer({ content }: MarkdownRendererProps) {
  useEffect(() => {
    document.querySelectorAll("pre code:not(.hljs)").forEach((el) => {
      hljs.highlightElement(el as HTMLElement);
    });
  }, [content]);

  return (
    <div className="markdown-content">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || "");
            const isInline = !match && !className;

            if (isInline) {
              return (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            }

            const lang = match?.[1] || "";
            let highlighted = String(children).replace(/\n$/, "");
            try {
              if (lang && hljs.getLanguage(lang)) {
                highlighted = hljs.highlight(highlighted, { language: lang }).value;
              }
            } catch {
              // fallback to plain text
            }

            return (
              <code
                className={`hljs ${lang ? `language-${lang}` : ""}`}
                dangerouslySetInnerHTML={{ __html: highlighted }}
                {...props}
              />
            );
          },
        }}
      />
    </div>
  );
}
