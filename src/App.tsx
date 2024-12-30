import React, { useState, useCallback } from 'react';
import Header from './components/Header';
import InputSection from './components/InputSection';
import NoteCard from './components/NoteCard';
import { useModelProcessing } from './hooks/useModelProcessing';
import { type Note } from './types';

export default function App() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [currentText, setCurrentText] = useState('');
  const { processText, isProcessing } = useModelProcessing();

  const handleProcessText = useCallback(async () => {
    const note = await processText(currentText);
    if (note) {
      setNotes(prev => [note, ...prev]);
      setCurrentText('');
    }
  }, [currentText, processText]);

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 transition-colors">
      <Header />
      
      <main className="max-w-4xl mx-auto px-4 py-8">
        <InputSection
          text={currentText}
          onTextChange={setCurrentText}
          onProcess={handleProcessText}
          isProcessing={isProcessing}
        />

        <div className="space-y-6">
          {notes.map(note => (
            <NoteCard key={note.id} note={note} />
          ))}
        </div>
      </main>

      <footer className="text-center py-6 text-gray-600 dark:text-gray-400">
        <p>© {new Date().getFullYear()} AI Note Taker. All rights reserved.</p>
      </footer>
    </div>
  );
}