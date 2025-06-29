const inputField = document.getElementById('chat-input');
const sendButton = document.getElementById('send-button');
const chatContainer = document.getElementById('chat-scroll-container');

function scrollToBottom() {
  window.scrollTo({
    top: document.body.scrollHeight,
    behavior: 'smooth'
  });
}

let currentChatId = null;

function getUserIdFromSession() {
  const userStr = sessionStorage.getItem('user');
  if (!userStr) return null;
  try {
    const user = JSON.parse(userStr);
    return user.id || null;
  } catch {
    return null;
  }
}
const userId = getUserIdFromSession();

function addChatBubble(text, from = 'user') {
  const bubble = document.createElement('div');
  bubble.className = `flex justify-${from === 'user' ? 'end' : 'start'} mt-4`;

  const innerBubble = document.createElement('div');
  const baseClass = "max-w-[70%] p-4 rounded-3xl text-[15px] font-normal shadow-md border";
  const botStyle = "bg-[#F0FDF4] text-[#0F5132] border-emerald-200 rounded-bl-none";
  const userStyle = "bg-[#DBFFEF] text-[#00885C] border-emerald-300/30 rounded-br-none";
  innerBubble.className = `${baseClass} ${from === 'user' ? userStyle : botStyle}`;

  if (from === 'bot') {
    const markdownContainer = document.createElement('div');
    markdownContainer.className = 'prose prose-sm max-w-none';
  try {
    markdownContainer.innerHTML = marked.parse(text);
  } catch (e) {
    markdownContainer.textContent = text;
  }

    innerBubble.appendChild(markdownContainer);
  } else {
    innerBubble.innerHTML = `<p>${text}</p>`;
  }

  bubble.appendChild(innerBubble);
  chatContainer.appendChild(bubble);
  // Panggil scrollToBottom setiap kali bubble baru ditambahkan
  scrollToBottom();
}


function showLoading() {
  const loadingBubble = document.createElement('div');
  loadingBubble.className = 'flex justify-start mt-2';
  loadingBubble.id = 'loading-bubble';
  const bubbleContent = document.createElement('div');
  bubbleContent.className = 'max-w-[70%] border border-white/20 p-4 rounded-3xl rounded-bl-none text-[16px] font-semibold shadow-md';
  bubbleContent.innerHTML = '<span class="dot-typing"><span></span><span></span><span></span></span>';
  loadingBubble.appendChild(bubbleContent);
  chatContainer.appendChild(loadingBubble);
  // Panggil scrollToBottom saat loading bubble muncul
  scrollToBottom();
}

async function sendMessage() {
  const userInput = inputField.value.trim();
  if (!userInput) return;

  addChatBubble(userInput, 'user');
  inputField.value = '';
  showLoading();

  try {
    // 1. Buat chat baru jika belum ada
    if (!currentChatId) {
      const chatTitle = userInput.length > 20 ? userInput.substring(0, 20) + "..." : userInput;
      const res = await fetch('https://epicare-fullstack.onrender.com/chat_history/chats', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, title: chatTitle })
      });
      const newChat = await res.json();
      currentChatId = newChat.id;
      fetchChatList();
    }

    // 2. Simpan pesan user ke backend
    await fetch('https://epicare-fullstack.onrender.com/chat_history/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: currentChatId, sender: 'user', content: userInput })
    });

    // 3. Ambil 3-4 pesan terakhir sebagai konteks
    const historyRes = await fetch(`https://epicare-fullstack.onrender.com/chat_history/messages/${currentChatId}`);
    const historyData = await historyRes.json();
    const lastMessages = historyData.slice(-4).map(msg => `${msg.sender === 'user' ? 'Pengguna' : 'Bot'}: ${msg.content}`);

const prompt = `
Kamu adalah Epicare, chatbot medis virtual yang bertugas memberikan informasi seputar Tuberkulosis (TBC) dan penyakit pernapasan serupa (misalnya pneumonia, PPOK, bronkiektasis, dan lainnya).

- Fokus hanya pada topik TBC dan penyakit terkait.
- Gunakan nada ramah, sopan, dan mudah dipahami, terutama untuk awam atau anak-anak.
- Jika menjawab dalam bentuk daftar, gejala, langkah, atau poin-poin, tolong gunakan format Markdown:
  - Gunakan tanda - atau * untuk membuat list
  - Gunakan **teks tebal** dengan tanda bintang dua
  - Gunakan heading dengan tanda ## untuk subjudul bila diperlukan
- Jangan gunakan HTML.
- Jangan terlalu kaku jika pengguna mengulang pertanyaan, tetap jawab saja seperti biasa seolah pengguna belum pernah menanyakan itu
- Jika pertanyaan tidak berkaitan dengan TBC atau penyakit serupa, jawab dengan sopan bahwa kamu hanya bisa membahas topik tersebut.
`;


    lastMessages.unshift(prompt);
    lastMessages.push(`Pengguna: ${userInput}`);

    // 4. Kirim ke Gemini
    const res = await fetch('https://epicare-fullstack.onrender.com/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: lastMessages })
    });
    const data = await res.json();
    document.getElementById('loading-bubble')?.remove();
    addChatBubble(data.reply || '⚠️ Respon kosong', 'bot');

    // 5. Simpan balasan bot
    await fetch('https://epicare-fullstack.onrender.com/chat_history/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: currentChatId, sender: 'bot', content: data.reply || '' })
    });

  } catch (err) {
    document.getElementById('loading-bubble')?.remove();
    addChatBubble('⚠️ Gagal menghubungi chatbot.', 'bot');
    console.error(err);
  }
}

sendButton.addEventListener('click', sendMessage);
inputField.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') sendMessage();
});

function addGreetingMessage() {
  addChatBubble("Hai! Saya Epicare. Saya bisa bantu menjelaskan gejala TBC dan penyakit pernapasan sejenis. Silakan tanya ya!", 'bot');
}

document.getElementById('new-chat-btn').addEventListener('click', () => {
  currentChatId = null;
  chatContainer.innerHTML = '';
  fetchChatList();
  addGreetingMessage();
});

async function fetchChatList() {
  try {
    console.log("Fetching chat list for userId:", userId);
    if (!userId) {
      console.error("User ID not found in sessionStorage.");
      document.getElementById('chat-history').innerHTML = '<p class="p-4">User not logged in. Please login again.</p>';
      return;
    }
    const res = await fetch(`https://epicare-fullstack.onrender.com/chat_history/chats/${userId}`);
    if (!res.ok) {
      console.error("Failed to fetch chat list, status:", res.status);
      throw new Error("Failed to fetch chat list");
    }
    const chats = await res.json();
    console.log("Chat list fetched:", chats);
    renderChatList(chats);
  } catch (error) {
    console.error(error);
    renderChatList([]);
  }
}

function renderChatList(chats) {
  const container = document.getElementById('chat-history');
  container.innerHTML = '';
  chats.forEach(chat => {
    const item = document.createElement('div');
    item.className = `p-3 bg-white/10 hover:bg-white/20 rounded-md cursor-pointer transition flex justify-between items-center ${
      chat.id === currentChatId ? 'border border-emerald-400' : ''
    }`;

    const titleContainer = document.createElement('div');
    titleContainer.className = 'flex items-center flex-grow cursor-pointer space-x-2';

    const titleText = document.createElement('div');
    titleText.className = 'text-gray-800 font-semibold mb-1';
    titleText.style.flex = '1 1 auto';
    titleText.style.fontSize = '14px';
    const maxTitleLength = 10;
    if (chat.title.length > maxTitleLength) {
      titleText.textContent = chat.title.substring(0, maxTitleLength) + '...';
    } else {
      titleText.textContent = chat.title;
    }

    const titleInput = document.createElement('input');
    titleInput.type = 'text';
    titleInput.value = chat.title;
    titleInput.className = 'hidden rounded px-2 py-1 text-black text-sm font-semibold w-full';

    titleContainer.appendChild(titleText);
    titleContainer.appendChild(titleInput);

    const createdAt = document.createElement('div');
    createdAt.className = 'text-sm 60';
    createdAt.textContent = new Date(chat.created_at).toLocaleDateString();

    const editButton = document.createElement('button');
    editButton.className = 'text-yellow-400 hover:text-yellow-600 ml-4';
    editButton.title = 'Edit judul percakapan';
    editButton.innerHTML = '<i class="fa-solid fa-pen-to-square"></i>';

    const deleteButton = document.createElement('button');
    deleteButton.className = 'text-red-500 hover:text-red-700 ml-4';
    deleteButton.title = 'Hapus percakapan';
    deleteButton.innerHTML = '<i class="fa-solid fa-trash"></i>';

    item.appendChild(titleContainer);
    item.appendChild(createdAt);
    item.appendChild(editButton);
    item.appendChild(deleteButton);

    editButton.addEventListener('click', (e) => {
      e.stopPropagation();
      titleText.classList.add('hidden');
      titleInput.classList.remove('hidden');
      titleInput.focus();
    });

    async function saveTitleUpdate() {
      const newTitle = titleInput.value.trim();
      if (newTitle === '') {
        alert('Judul tidak boleh kosong.');
        titleInput.value = chat.title;
        titleInput.classList.add('hidden');
        titleText.classList.remove('hidden');
        return;
      }
      if (newTitle === chat.title) {
        titleInput.classList.add('hidden');
        titleText.classList.remove('hidden');
        return;
      }
      try {
        const res = await fetch(`https://epicare-fullstack.onrender.com/chat_history/chats/${chat.id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title: newTitle })
        });
        if (!res.ok) throw new Error('Gagal memperbarui judul');
        const updatedChat = await res.json();
        chat.title = updatedChat.title;
        if (updatedChat.title.length > maxTitleLength) {
          titleText.textContent = updatedChat.title.substring(0, maxTitleLength) + '...';
        } else {
          titleText.textContent = updatedChat.title;
        }
      } catch (error) {
        alert('Gagal memperbarui judul. Silakan coba lagi.');
        console.error(error);
        titleInput.value = chat.title;
      } finally {
        titleInput.classList.add('hidden');
        titleText.classList.remove('hidden');
      }
    }

    titleInput.addEventListener('blur', saveTitleUpdate);
    titleInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        titleInput.blur();
      }
    });

    deleteButton.addEventListener('click', async (e) => {
      e.stopPropagation();
      if (!confirm('Apakah Anda yakin ingin menghapus percakapan ini?')) return;
      try {
        const res = await fetch(`https://epicare-fullstack.onrender.com/chat_history/chats/${chat.id}`, {
          method: 'DELETE',
        });
        if (!res.ok) throw new Error('Gagal menghapus percakapan');
        if (chat.id === currentChatId) {
          currentChatId = null;
          chatContainer.innerHTML = '';
        }
        fetchChatList();
      } catch (error) {
        alert('Gagal menghapus percakapan. Silakan coba lagi.');
        console.error(error);
      }
    });

    item.onclick = () => loadChat(chat.id);

    container.appendChild(item);
  });
}

async function loadChat(chatId) {
  currentChatId = chatId;

  chatContainer.innerHTML = '';

  try {
    const res = await fetch(`https://epicare-fullstack.onrender.com/chat_history/messages/${chatId}`);
    if (!res.ok) throw new Error("Failed to fetch messages");
    const messages = await res.json();
    messages.forEach(msg => addChatBubble(msg.content, msg.sender));
  } catch (error) {
    console.error(error);
    addChatBubble("⚠️ Gagal memuat pesan chat.", "bot");
  }

  fetchChatList();
}

document.getElementById('new-chat-btn').addEventListener('click', () => {
  currentChatId = null;
  chatContainer.innerHTML = '';
  addGreetingMessage();

  // Hindari mengambil chat lama setelah reset
  if (typeof fetchChatList === 'function') {
    fetchChatList(); // hanya update daftar riwayat di sidebar
  }

  // Bersihkan local cache chat dari sesi sebelumnya (opsional)
  sessionStorage.removeItem('lastMessages');
});

fetchChatList();
addGreetingMessage();

function formatPlainTextToHTML(text) {
  const lines = text.split('\n');
  let html = '';
  let inList = false;

  for (let line of lines) {
    const trimmed = line.trim();
    if (trimmed === '') {
      if (inList) {
        html += '</ul>';
        inList = false;
      }
      html += '<br>';
      continue;
    }

    if (/^[-*•]\s+/.test(trimmed)) {
      if (!inList) {
        html += '<ul class="list-disc pl-6">';
        inList = true;
      }
      html += `<li>${trimmed.replace(/^[-*•]\s+/, '')}</li>`;
    } else {
      if (inList) {
        html += '</ul>';
        inList = false;
      }
      html += `<p>${trimmed}</p>`;
    }
  }

  if (inList) html += '</ul>';
  return html;
}