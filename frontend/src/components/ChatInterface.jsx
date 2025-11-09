import React, { useState, useRef, useEffect } from 'react';
import {
  Paper,
  Box,
  TextField,
  Button,
  Typography,
  CircularProgress,
  Avatar,
  Chip
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "👋 Hello! I'm HomeWise AI, your Australian property expert. I can help you with:\n\n• Estimating property prices\n• Calculating your buying power\n• Understanding market trends\n• Answering property questions\n\nWhat would you like to know?",
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_URL}/api/chat`, {
        message: inputMessage,
        conversation_history: messages.map(msg => ({
          role: msg.role,
          content: msg.content
        }))
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.data.message,
        data: response.data.data,
        agent_used: response.data.agent_used,
        sources: response.data.sources,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: "I apologize, but I'm having trouble connecting to the server. Please make sure the backend is running and try again.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatCurrency = (value) => {
    if (!value) return 'N/A';
    return new Intl.NumberFormat('en-AU', {
      style: 'currency',
      currency: 'AUD',
      minimumFractionDigits: 0
    }).format(value);
  };

  const renderMessageContent = (message) => {
    const content = message.content;

    // Render data if available (for price estimates, buying power, etc.)
    if (message.data) {
      if (message.agent_used === 'price_estimation') {
        return (
          <Box>
            <Typography variant="body1" paragraph>
              {content}
            </Typography>
            <Paper elevation={1} sx={{ p: 2, mt: 2, bgcolor: '#e3f2fd' }}>
              <Typography variant="h6" gutterBottom>
                Price Estimate Details
              </Typography>
              <Box sx={{ display: 'grid', gap: 1 }}>
                <Typography>
                  <strong>Estimated Price:</strong> {formatCurrency(message.data.estimated_price)}
                </Typography>
                <Typography>
                  <strong>Price Range:</strong> {formatCurrency(message.data.price_range_min)} - {formatCurrency(message.data.price_range_max)}
                </Typography>
                <Typography>
                  <strong>Confidence:</strong> {(message.data.confidence_score * 100).toFixed(0)}%
                </Typography>
              </Box>
            </Paper>
          </Box>
        );
      } else if (message.agent_used === 'buying_power') {
        return (
          <Box>
            <Typography variant="body1" paragraph>
              {content}
            </Typography>
            <Paper elevation={1} sx={{ p: 2, mt: 2, bgcolor: '#e8f5e9' }}>
              <Typography variant="h6" gutterBottom>
                Buying Power Summary
              </Typography>
              <Box sx={{ display: 'grid', gap: 1 }}>
                <Typography>
                  <strong>Maximum Property Price:</strong> {formatCurrency(message.data.max_property_price)}
                </Typography>
                <Typography>
                  <strong>Maximum Loan:</strong> {formatCurrency(message.data.max_loan_amount)}
                </Typography>
                <Typography>
                  <strong>Monthly Repayment:</strong> {formatCurrency(message.data.monthly_repayment)}
                </Typography>
                <Typography>
                  <strong>LVR:</strong> {message.data.loan_to_value_ratio}%
                </Typography>
                <Typography>
                  <strong>Total Upfront Costs:</strong> {formatCurrency(message.data.total_upfront_costs)}
                </Typography>
                <Typography>
                  <strong>Affordability Rating:</strong> {message.data.affordability_rating}
                </Typography>
              </Box>
            </Paper>
          </Box>
        );
      }
    }

    // Default rendering for text
    return (
      <Typography variant="body1" style={{ whiteSpace: 'pre-wrap' }}>
        {content}
      </Typography>
    );
  };

  return (
    <Paper elevation={3} sx={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
      {/* Messages Container */}
      <Box
        sx={{
          flexGrow: 1,
          overflowY: 'auto',
          p: 2,
          bgcolor: '#fafafa'
        }}
      >
        {messages.map((message, index) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              mb: 2,
              alignItems: 'flex-start',
              justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start'
            }}
          >
            {message.role === 'assistant' && (
              <Avatar sx={{ bgcolor: '#1976d2', mr: 1 }}>
                <SmartToyIcon />
              </Avatar>
            )}

            <Box sx={{ maxWidth: '70%' }}>
              <Paper
                elevation={1}
                sx={{
                  p: 2,
                  bgcolor: message.role === 'user' ? '#1976d2' : '#fff',
                  color: message.role === 'user' ? '#fff' : '#000'
                }}
              >
                {renderMessageContent(message)}
              </Paper>

              {message.sources && message.sources.length > 0 && (
                <Box sx={{ mt: 1, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                  {message.sources.map((source, idx) => (
                    <Chip key={idx} label={source} size="small" variant="outlined" />
                  ))}
                </Box>
              )}
            </Box>

            {message.role === 'user' && (
              <Avatar sx={{ bgcolor: '#dc004e', ml: 1 }}>
                <PersonIcon />
              </Avatar>
            )}
          </Box>
        ))}

        {isLoading && (
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Avatar sx={{ bgcolor: '#1976d2', mr: 1 }}>
              <SmartToyIcon />
            </Avatar>
            <Paper elevation={1} sx={{ p: 2 }}>
              <CircularProgress size={20} />
              <Typography variant="body2" sx={{ ml: 1, display: 'inline' }}>
                Thinking...
              </Typography>
            </Paper>
          </Box>
        )}

        <div ref={messagesEndRef} />
      </Box>

      {/* Input Area */}
      <Box sx={{ p: 2, bgcolor: '#fff', borderTop: '1px solid #e0e0e0' }}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Ask me about property prices, buying power, or market trends..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
            multiline
            maxRows={3}
          />
          <Button
            variant="contained"
            endIcon={<SendIcon />}
            onClick={handleSendMessage}
            disabled={isLoading || !inputMessage.trim()}
            sx={{ minWidth: '100px' }}
          >
            Send
          </Button>
        </Box>
      </Box>
    </Paper>
  );
};

export default ChatInterface;
