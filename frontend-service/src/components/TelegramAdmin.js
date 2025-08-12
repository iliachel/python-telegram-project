import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

const TelegramAdmin = () => {
    // State for sending a message to a single user
    const [userId, setUserId] = useState('');
    const [messageText, setMessageText] = useState('');
    const [sendToUserStatus, setSendToUserStatus] = useState('');

    // State for broadcasting a message
    const [broadcastMessage, setBroadcastMessage] = useState('');
    const [broadcastStatus, setBroadcastStatus] = useState('');

    // State for chat history
    const [chatHistory, setChatHistory] = useState([]);
    const [historyError, setHistoryError] = useState('');

    // Fetch chat history
    const fetchChatHistory = useCallback(async () => {
        try {
            const response = await axios.get(`${API_URL}/telegram/chat_history`, { withCredentials: true });
            setChatHistory(response.data);
            setHistoryError('');
        } catch (error) {
            setHistoryError('Failed to fetch chat history.');
            console.error(error);
        }
    }, []);

    // Poll for chat history every 5 seconds
    useEffect(() => {
        fetchChatHistory();
        const interval = setInterval(fetchChatHistory, 5000);
        return () => clearInterval(interval);
    }, [fetchChatHistory]);

    // Handler for sending a message to a single user
    const handleSendToUser = async (e) => {
        e.preventDefault();
        setSendToUserStatus('Sending...');
        try {
            const response = await axios.post(`${API_URL}/telegram/send_message`, { user_id: userId, text: messageText }, { withCredentials: true });
            setSendToUserStatus(`Message sent: ${response.data.status}`);
        } catch (error) {
            setSendToUserStatus('Failed to send message.');
            console.error(error);
        }
    };

    // Handler for broadcasting a message
    const handleBroadcast = async (e) => {
        e.preventDefault();
        setBroadcastStatus('Broadcasting...');
        try {
            const response = await axios.post(`${API_URL}/telegram/broadcast`, { text: broadcastMessage }, { withCredentials: true });
            setBroadcastStatus(`Broadcast result: ${response.data.status} (Sent: ${response.data.sent}, Failed: ${response.data.failed})`);
        } catch (error) {
            setBroadcastStatus('Failed to broadcast message.');
            console.error(error);
        }
    };

    return (
        <div>
            <h3>Telegram Administration</h3>

            {/* Chat History Section */}
            <div style={{ border: '1px solid #ccc', padding: '10px', marginBottom: '20px', maxHeight: '300px', overflowY: 'scroll' }}>
                <h4>Chat History</h4>
                {historyError && <p style={{ color: 'red' }}>{historyError}</p>}
                {chatHistory.length > 0 ? (
                    chatHistory.map((msg, index) => (
                        <p key={index}><b>{msg.username || 'Unknown'}</b>: {msg.text}</p>
                    ))
                ) : (
                    <p>No chat history available.</p>
                )}
            </div>

            {/* Send Message to User Section */}
            <div style={{ border: '1px solid #ccc', padding: '10px', marginBottom: '20px' }}>
                <h4>Send Message to User</h4>
                <form onSubmit={handleSendToUser}>
                    <div>
                        <label>User ID (Chat ID):</label>
                        <input type="text" value={userId} onChange={(e) => setUserId(e.target.value)} required />
                    </div>
                    <div>
                        <label>Message:</label>
                        <input type="text" value={messageText} onChange={(e) => setMessageText(e.target.value)} required />
                    </div>
                    <button type="submit">Send Message</button>
                </form>
                {sendToUserStatus && <p>{sendToUserStatus}</p>}
            </div>

            {/* Broadcast Message Section */}
            <div style={{ border: '1px solid #ccc', padding: '10px' }}>
                <h4>Send Message to Everyone (Broadcast)</h4>
                <form onSubmit={handleBroadcast}>
                    <div>
                        <label>Broadcast Message:</label>
                        <input type="text" value={broadcastMessage} onChange={(e) => setBroadcastMessage(e.target.value)} required style={{ width: '300px' }}/>
                    </div>
                    <button type="submit">Send to Everyone</button>
                </form>
                {broadcastStatus && <p>{broadcastStatus}</p>}
            </div>
        </div>
    );
};

export default TelegramAdmin;
