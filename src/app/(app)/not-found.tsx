import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-3 px-6 text-center">
      <p className="text-sm font-medium">Esta conversación no existe.</p>
      <p className="max-w-sm text-sm text-neutral-500">
        Puede que se haya borrado, o que el enlace sea de la conversación de otra persona.
      </p>
      <Link
        href="/"
        className="rounded-md bg-neutral-900 px-3 py-2 text-sm font-medium text-white dark:bg-neutral-100 dark:text-neutral-900"
      >
        Empezar una conversación nueva
      </Link>
    </div>
  );
}
