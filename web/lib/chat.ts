export async function sendChatMessage(message: string): Promise<string> {
  const res = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, show_thinking: true }),
  });
  if (!res.ok) {
    throw new Error('Network response was not ok');
  }
  const data = await res.json();
  return data.answer || '';
}
