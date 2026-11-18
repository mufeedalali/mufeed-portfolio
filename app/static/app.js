/* Frontend JavaScript client with streaming SSE handling */

class RAGClient {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl || '';
        this.topK = 5;
        this.llmProvider = 'mock';
        this.temperature = 0.7;
    }

    async uploadDocument(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${this.baseUrl}/documents/upload`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail?.error || 'Upload failed');
        }

        return await response.json();
    }

    async listDocuments() {
        const response = await fetch(`${this.baseUrl}/documents/`);

        if (!response.ok) {
            throw new Error('Failed to list documents');
        }

        return await response.json();
    }

    async deleteDocument(documentId) {
        const response = await fetch(`${this.baseUrl}/documents/${documentId}`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            throw new Error('Failed to delete document');
        }

        return await response.json();
    }

    async query(queryText, documentId = null) {
        const payload = {
            query: queryText,
            document_id: documentId,
        };

        const response = await fetch(`${this.baseUrl}/rag/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail?.error || 'Query failed');
        }

        return await response.json();
    }

    async queryStream(queryText, onChunk, onCitations, documentId = null) {
        const payload = {
            query: queryText,
            document_id: documentId,
        };

        const response = await fetch(`${this.baseUrl}/rag/query/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail?.error || 'Stream query failed');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        try {
            while (true) {
                const { done, value } = await reader.read();

                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.substring(6));

                            if (data.type === 'citations' && onCitations) {
                                onCitations(data.data.citations);
                            } else if (data.type === 'chunk' && onChunk) {
                                onChunk(data.data.text);
                            } else if (data.type === 'error') {
                                throw new Error(data.data.error);
                            }
                        } catch (e) {
                            console.error('Error parsing stream data:', e);
                        }
                    }
                }
            }
        } finally {
            reader.releaseLock();
        }
    }

    async chatStream(messageText, onChunk, onCitations, documentId = null) {
        return this.queryStream(messageText, onChunk, onCitations, documentId);
    }
}

// UI Controller
class UIController {
    constructor() {
        this.client = new RAGClient();
        this.selectedDocumentId = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDocuments();
        this.loadSettings();
    }

    setupEventListeners() {
        // Upload area
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');

        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            this.handleFiles(e.dataTransfer.files);
        });

        fileInput.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
            e.target.value = '';
        });

        // Query form
        const queryForm = document.getElementById('chatForm');
        queryForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleQuery();
        });

        // Settings
        document.getElementById('topK').addEventListener('change', (e) => {
            this.client.topK = parseInt(e.target.value);
            localStorage.setItem('topK', e.target.value);
        });

        document.getElementById('llmProvider').addEventListener('change', (e) => {
            this.client.llmProvider = e.target.value;
            localStorage.setItem('llmProvider', e.target.value);
        });

        document.getElementById('temperature').addEventListener('change', (e) => {
            this.client.temperature = parseFloat(e.target.value);
            document.getElementById('tempValue').textContent = e.target.value;
            localStorage.setItem('temperature', e.target.value);
        });
    }

    loadSettings() {
        const topK = localStorage.getItem('topK') || '5';
        const llmProvider = localStorage.getItem('llmProvider') || 'mock';
        const temperature = localStorage.getItem('temperature') || '0.7';

        document.getElementById('topK').value = topK;
        document.getElementById('llmProvider').value = llmProvider;
        document.getElementById('temperature').value = temperature;
        document.getElementById('tempValue').textContent = temperature;

        this.client.topK = parseInt(topK);
        this.client.llmProvider = llmProvider;
        this.client.temperature = parseFloat(temperature);
    }

    async handleFiles(files) {
        for (const file of files) {
            await this.uploadDocument(file);
        }
    }

    async uploadDocument(file) {
        const spinner = document.getElementById('spinner');
        spinner.style.display = 'block';

        try {
            await this.client.uploadDocument(file);
            this.showMessage(`Uploaded ${file.name}`, 'success');
            await this.loadDocuments();
        } catch (error) {
            this.showError(`Upload failed: ${error.message}`);
        } finally {
            spinner.style.display = 'none';
        }
    }

    async loadDocuments() {
        try {
            const response = await this.client.listDocuments();
            const documentList = document.getElementById('documentList');

            if (response.documents.length === 0) {
                documentList.innerHTML = '<p class="empty-state">No documents yet</p>';
                return;
            }

            documentList.innerHTML = response.documents.map(doc => `
                <div class="document-item">
                    <span class="document-name" title="${doc.filename}">${doc.filename}</span>
                    <span class="document-status ${doc.status}">${doc.status}</span>
                    <button class="document-delete" onclick="ui.deleteDocument('${doc.id}')">✕</button>
                </div>
            `).join('');
        } catch (error) {
            this.showError(`Failed to load documents: ${error.message}`);
        }
    }

    async deleteDocument(documentId) {
        if (!confirm('Delete this document?')) return;

        try {
            await this.client.deleteDocument(documentId);
            this.showMessage('Document deleted', 'success');
            await this.loadDocuments();
        } catch (error) {
            this.showError(`Delete failed: ${error.message}`);
        }
    }

    async handleQuery() {
        const queryInput = document.getElementById('queryInput');
        const query = queryInput.value.trim();

        if (!query) return;

        queryInput.value = '';
        this.addMessage(query, 'user');

        const spinner = document.getElementById('spinner');
        spinner.style.display = 'block';

        try {
            let fullAnswer = '';
            let citations = [];

            await this.client.queryStream(
                query,
                (chunk) => {
                    fullAnswer += chunk;
                    this.updateLastMessage(fullAnswer);
                },
                (newCitations) => {
                    citations = newCitations;
                    if (citations.length > 0) {
                        const citationText = citations
                            .map(c => `${c.document_name} (relevance: ${(c.relevance_score * 100).toFixed(0)}%)`)
                            .join(' • ');
                        this.addCitationsToLastMessage(citationText, citations);
                    }
                },
                this.selectedDocumentId
            );
        } catch (error) {
            this.showError(`Query failed: ${error.message}`);
            this.addMessage('Error: ' + error.message, 'assistant');
        } finally {
            spinner.style.display = 'none';
        }
    }

    addMessage(text, role) {
        const chatMessages = document.getElementById('chatMessages');
        const messageEl = document.createElement('div');
        messageEl.className = `message ${role}-message`;
        messageEl.innerHTML = `
            <div class="message-content">
                <p>${this.escapeHtml(text)}</p>
            </div>
        `;
        messageEl.id = `message-${Date.now()}`;
        chatMessages.appendChild(messageEl);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    updateLastMessage(text) {
        const chatMessages = document.getElementById('chatMessages');
        const lastMessage = chatMessages.querySelector('.assistant-message:last-of-type');

        if (lastMessage) {
            const content = lastMessage.querySelector('.message-content p');
            content.textContent = text;
        } else {
            this.addMessage(text, 'assistant');
        }

        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    addCitationsToLastMessage(citationText, citations) {
        const chatMessages = document.getElementById('chatMessages');
        const lastMessage = chatMessages.querySelector('.assistant-message:last-of-type');

        if (lastMessage) {
            let citationsEl = lastMessage.querySelector('.message-citations');
            if (!citationsEl) {
                citationsEl = document.createElement('div');
                citationsEl.className = 'message-citations';
                lastMessage.appendChild(citationsEl);
            }
            citationsEl.innerHTML = `<strong>Sources:</strong><br>` +
                citations.map(c => `<div class="citation-item">${this.escapeHtml(c.document_name)} (${(c.relevance_score * 100).toFixed(0)}%)</div>`).join('');
        }
    }

    showMessage(text, type = 'info') {
        console.log(`[${type}] ${text}`);
    }

    showError(error) {
        const errorToast = document.getElementById('errorToast');
        errorToast.textContent = error;
        errorToast.style.display = 'block';

        setTimeout(() => {
            errorToast.style.display = 'none';
        }, 5000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize UI
let ui;
document.addEventListener('DOMContentLoaded', () => {
    ui = new UIController();
});
