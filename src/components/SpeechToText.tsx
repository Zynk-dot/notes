import React, { useState, useEffect, useCallback } from 'react';
import { Mic, MicOff } from 'lucide-react';

interface Props {
  onTranscript: (text: string) => void;
}

export default function SpeechToText({ onTranscript }: Props) {
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState<SpeechRecognition | null>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        setRecognition(recognition);
      }
    }
  }, []);

  const startListening = useCallback(() => {
    if (recognition) {
      recognition.onresult = (event: SpeechRecognitionEvent) => {
        const transcript = Array.from(event.results)
          .map(result => result[0].transcript)
          .join('');
        onTranscript(transcript);
      };
      recognition.start();
      setIsListening(true);
    }
  }, [recognition, onTranscript]);

  const stopListening = useCallback(() => {
    if (recognition) {
      recognition.stop();
      setIsListening(false);
    }
  }, [recognition]);

  return (
    <button
      onClick={isListening ? stopListening : startListening}
      className={`p-3 rounded-full ${
        isListening ? 'bg-red-500 hover:bg-red-600' : 'bg-blue-500 hover:bg-blue-600'
      } text-white transition-colors`}
      title={isListening ? 'Stop recording' : 'Start recording'}
    >
      {isListening ? <MicOff size={24} /> : <Mic size={24} />}
    </button>
  );
}