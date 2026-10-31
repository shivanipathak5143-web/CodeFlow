export function ErrorNote({ message }: { message: string | null }) {
  if (!message) return null;
  return (
    <p className="note note--error" role="alert">
      {message}
    </p>
  );
}