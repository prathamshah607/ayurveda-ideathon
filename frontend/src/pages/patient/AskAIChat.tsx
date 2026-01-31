import React, { useState, useRef, useEffect } from 'react';
import { Send, Leaf, User, Sparkles } from 'lucide-react';
import { Card, Button } from '../../components/ui';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const suggestedQuestions = [
  'What foods should I eat for my Prakriti?',
  'How can I improve my sleep naturally?',
  'What herbs are good for stress relief?',
  'How do I balance Vata dosha?',
  'What is the best daily routine for me?',
];

const initialMessages: Message[] = [
  {
    id: '1',
    role: 'assistant',
    content: "Namaste! 🙏 I'm your Ayurveda AI assistant. I can help you with questions about Ayurvedic principles, diet recommendations based on your Prakriti, lifestyle tips, and general wellness guidance. How can I assist you today?",
    timestamp: new Date(),
  },
];

export function AskAIChat() {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (message: string) => {
    if (!message.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: message,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate AI response
    await new Promise((resolve) => setTimeout(resolve, 1500));

    const aiResponse = getAIResponse(message);
    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: aiResponse,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, assistantMessage]);
    setIsTyping(false);
  };

  const getAIResponse = (question: string): string => {
    const lowerQuestion = question.toLowerCase();

    if (lowerQuestion.includes('food') || lowerQuestion.includes('diet') || lowerQuestion.includes('eat')) {
      return `Based on your Vata-Pitta Prakriti, here are my dietary recommendations:

**Foods to Favor:**
- Warm, cooked meals with healthy fats (ghee, coconut oil)
- Sweet fruits like bananas, mangoes, and grapes
- Cooked vegetables like sweet potatoes, carrots, and beets
- Whole grains like rice and oats
- Mild spices like ginger, cumin, and coriander

**Foods to Reduce:**
- Cold, raw, and dry foods
- Excessive spicy, sour, or salty foods
- Caffeine and stimulants
- Processed and frozen foods

Would you like more specific meal ideas? 🍽️`;
    }

    if (lowerQuestion.includes('sleep') || lowerQuestion.includes('insomnia')) {
      return `Great question! Here are Ayurvedic tips for better sleep:

**Evening Routine:**
1. Eat a light dinner before 7 PM
2. Avoid screens 1-2 hours before bed
3. Practice gentle yoga or stretching
4. Take a warm bath with relaxing herbs

**Before Bed:**
- Drink warm milk with a pinch of nutmeg
- Apply warm oil to your feet (Padabhyanga)
- Practice 10 minutes of deep breathing

**Sleep Timing:**
According to Ayurveda, the ideal sleep time is 10 PM - 6 AM, aligning with natural Kapha time for deep, restorative rest.

Would you like guidance on specific practices? 🌙`;
    }

    if (lowerQuestion.includes('stress') || lowerQuestion.includes('anxiety')) {
      return `Managing stress is crucial for your Vata-Pitta constitution. Here's what I recommend:

**Herbs for Stress:**
- **Ashwagandha**: Adaptogenic, calms the nervous system
- **Brahmi**: Supports mental clarity and reduces anxiety
- **Jatamansi**: Natural sedative, promotes peace

**Daily Practices:**
- Morning meditation (even 10 minutes helps)
- Pranayama: Practice Anulom Vilom and Bhramari
- Regular Abhyanga (self-massage) with warm sesame oil
- Spend time in nature

**Lifestyle Tips:**
- Maintain regular routines
- Reduce commitments and prioritize rest
- Limit social media and news consumption

Would you like a guided breathing exercise? 🧘`;
    }

    if (lowerQuestion.includes('vata') || lowerQuestion.includes('balance')) {
      return `To balance Vata dosha, focus on qualities opposite to Vata (which is cold, dry, light, and mobile):

**Balancing Strategies:**
1. **Warmth**: Stay warm, avoid cold environments
2. **Moisture**: Use oils liberally (internally and externally)
3. **Grounding**: Maintain steady routines
4. **Nourishment**: Eat warm, cooked, substantive foods

**Daily Routine (Dinacharya):**
- Wake before sunrise
- Oil massage (Abhyanga) before shower
- Warm breakfast with healthy fats
- Gentle exercise (yoga, walking)
- Regular meal times
- Early, warm dinner
- Calming evening routine
- Sleep by 10 PM

This creates the stability Vata needs. Shall I elaborate on any aspect? 🍃`;
    }

    return `That's an interesting question! Let me share some Ayurvedic perspective:

Ayurveda, the "Science of Life," offers a holistic approach to health that considers your unique constitution (Prakriti), current imbalances (Vikriti), and lifestyle factors.

Based on your profile as a Vata-Pitta individual, the key principles for you are:
- **Regularity**: Maintain consistent daily routines
- **Warmth**: Favor warm foods and environments
- **Calm**: Prioritize stress management
- **Nourishment**: Choose grounding, nourishing foods

I'd be happy to provide more specific guidance. Could you tell me more about what aspect of your health you'd like to focus on? 🌿`;
  };

  return (
    <div className="animate-fade-in h-[calc(100vh-12rem)] flex flex-col">
      <div className="mb-4">
        <h1 className="font-heading text-2xl font-bold text-text-primary">Ask AI</h1>
        <p className="text-text-secondary">Chat with your personal Ayurveda AI assistant</p>
      </div>

      <Card className="flex-1 flex flex-col overflow-hidden">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex items-start gap-3 ${
                message.role === 'user' ? 'flex-row-reverse' : ''
              }`}
            >
              {/* Avatar */}
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  message.role === 'assistant' ? 'bg-primary' : 'bg-accent'
                }`}
              >
                {message.role === 'assistant' ? (
                  <Leaf className="text-white" size={16} />
                ) : (
                  <User className="text-white" size={16} />
                )}
              </div>

              {/* Message Bubble */}
              <div
                className={`max-w-[70%] rounded-2xl px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-primary text-white rounded-tr-sm'
                    : 'bg-gray-100 text-text-primary rounded-tl-sm'
                }`}
              >
                <div className="whitespace-pre-wrap text-sm">{message.content}</div>
                <p
                  className={`text-xs mt-2 ${
                    message.role === 'user' ? 'text-white/70' : 'text-text-secondary'
                  }`}
                >
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            </div>
          ))}

          {/* Typing indicator */}
          {isTyping && (
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                <Leaf className="text-white" size={16} />
              </div>
              <div className="bg-gray-100 rounded-2xl rounded-tl-sm px-4 py-3">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Questions */}
        {messages.length <= 2 && (
          <div className="px-4 py-3 border-t border-gray-100">
            <p className="text-xs text-text-secondary mb-2 flex items-center gap-1">
              <Sparkles size={12} />
              Suggested questions
            </p>
            <div className="flex flex-wrap gap-2">
              {suggestedQuestions.map((question) => (
                <button
                  key={question}
                  onClick={() => handleSend(question)}
                  className="px-3 py-1.5 text-xs bg-primary/5 text-primary rounded-full hover:bg-primary/10 transition-colors"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input */}
        <div className="p-4 border-t border-gray-100">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend(inputValue);
            }}
            className="flex gap-3"
          >
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask about Ayurveda, diet, lifestyle..."
              className="flex-1 px-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
              disabled={isTyping}
            />
            <Button
              type="submit"
              disabled={!inputValue.trim() || isTyping}
              className="px-6"
            >
              <Send size={20} />
            </Button>
          </form>
          <p className="text-xs text-text-secondary text-center mt-2">
            AI responses are for informational purposes only. Consult a healthcare provider for medical advice.
          </p>
        </div>
      </Card>
    </div>
  );
}
