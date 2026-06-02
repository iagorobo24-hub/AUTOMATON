/**
 * @param {{ code: string, language?: string }} props
 */
export default function CodeBlock({ code, language = 'json' }) {
  // Try to format JSON if possible
  const formattedCode = (() => {
    if (language === 'json') {
      try {
        const parsed = JSON.parse(code);
        return JSON.stringify(parsed, null, 2);
      } catch {
        return code;
      }
    }
    return code;
  })();

  return (
    <pre className="code-block overflow-auto max-h-[300px]">
      <code>{formattedCode}</code>
    </pre>
  );
}
