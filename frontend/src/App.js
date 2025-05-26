import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import { CircularProgress } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import ImageIcon from '@mui/icons-material/Image';

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f5f5f5;
`;

const ChatContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
`;

const MessageContainer = styled.div`
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
  align-items: ${props => props.isUser ? 'flex-end' : 'flex-start'};
`;

const MessageBubble = styled.div`
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 15px;
  background-color: ${props => props.isUser ? '#007bff' : '#e9ecef'};
  color: ${props => props.isUser ? 'white' : 'black'};
  margin-bottom: 8px;
`;

const ImageContainer = styled.div`
  position: relative;
  max-width: 300px;
  margin-top: 8px;
  border-radius: 10px;
  overflow: hidden;
  background-color: #f8f9fa;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const MessageImage = styled.img`
  max-width: 100%;
  border-radius: 10px;
  opacity: ${props => props.loaded ? 1 : 0};
  transition: opacity 0.3s ease-in-out;
`;

const ImagePlaceholder = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #6c757d;
  gap: 8px;
`;

const InputContainer = styled.div`
  display: flex;
  gap: 10px;
  padding: 10px;
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
`;

const Input = styled.input`
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 16px;
  &:focus {
    outline: none;
    border-color: #007bff;
  }
`;

const SendButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  &:disabled {
    background-color: #ccc;
  }
`;

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [imageLoading, setImageLoading] = useState({});
  const chatContainerRef = useRef(null);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const handleImageLoad = (messageIndex) => {
    setImageLoading(prev => ({
      ...prev,
      [messageIndex]: false
    }));
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { text: userMessage, isUser: true }]);
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:5000/api/chat', {
        message: userMessage
      });

      const newMessageIndex = messages.length + 1;
      if (response.data.image_url) {
        setImageLoading(prev => ({
          ...prev,
          [newMessageIndex]: true
        }));
      }

      setMessages(prev => [...prev, {
        text: response.data.message,
        isUser: false,
        imageUrl: response.data.image_url
      }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        text: 'Sorry, something went wrong. Please try again.',
        isUser: false
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <AppContainer>
      <ChatContainer ref={chatContainerRef}>
        {messages.map((message, index) => (
          <MessageContainer key={index} isUser={message.isUser}>
            <MessageBubble isUser={message.isUser}>
              {message.text}
            </MessageBubble>
            {message.imageUrl && (
              <ImageContainer>
                {imageLoading[index] && (
                  <ImagePlaceholder>
                    <CircularProgress size={24} />
                    <span>Generating image...</span>
                  </ImagePlaceholder>
                )}
                <MessageImage
                  src={message.imageUrl}
                  alt="Generated story illustration"
                  loaded={!imageLoading[index]}
                  onLoad={() => handleImageLoad(index)}
                  onError={() => handleImageLoad(index)}
                />
              </ImageContainer>
            )}
          </MessageContainer>
        ))}
        {loading && (
          <MessageContainer>
            <CircularProgress size={24} />
          </MessageContainer>
        )}
      </ChatContainer>
      <InputContainer>
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask me about the stories..."
          disabled={loading}
        />
        <SendButton onClick={handleSend} disabled={loading || !input.trim()}>
          <SendIcon />
        </SendButton>
      </InputContainer>
    </AppContainer>
  );
}

export default App; 