import { sendChatMessage } from '../lib/chat';

describe('sendChatMessage', () => {
  it('sends a message and returns the answer', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ answer: 'hi' }),
    });

    const result = await sendChatMessage('hello');

    expect(fetch).toHaveBeenCalled();
    expect(result).toBe('hi');
  });
});
