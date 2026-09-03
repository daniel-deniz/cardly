export function TypingIndicator() {
  return (
    <span className="flex items-center gap-1 px-1 py-0.5" aria-label="Cardly está escribiendo">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="size-1.5 rounded-full bg-neutral-400"
          style={{ animation: `cardly-punto 1.2s ${i * 0.15}s infinite ease-in-out` }}
        />
      ))}
    </span>
  );
}
