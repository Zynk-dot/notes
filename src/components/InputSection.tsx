import React from 'react';
import { ListChecks, Loader2 } from 'lucide-react';
import SpeechToText from './SpeechToText';

interface Props {
  text: string;
  onTextChange: (text: string) => void;
  onProcess: () => void;
  isProcessing: boolean;
}

export default function InputSection({ text, onTextChange, onProcess, isProcessing }: Props) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-8">
      <div className="flex items-start space-x-4">
        <SpeechToText onTranscript={onTextChange} />
        <div className="flex-1">
          <textarea
            value={text}
            onChange={(e) => onTextChange(e.target.value)}
            placeholder="Start speaking or type your notes here..."
            className="w-full h-32 p-3 border border-gray-300 dark:border-gray-600 rounded-lg 
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100
                     focus:ring-2 focus:ring-blue-500 focus:border-transparent
                     transition-colors"
          />
        </div>
      </div>
      
      <div className="mt-4 flex justify-end">
        <button
          onClick={onProcess}
          disabled={isProcessing || !text.trim()}
          className="flex items-center px-4 py-2 bg-blue-500 hover:bg-blue-600 
                   text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed
                   transition-colors"
        >
          {isProcessing ? (
            <>
              <Loader2 className="animate-spin mr-2" size={20} />
              Processing...
            </>
          ) : (
            <>
              <ListChecks className="mr-2" size={20} />
              Process Note
            </>
          )}
        </button>
      </div>
    </div>
  );
}