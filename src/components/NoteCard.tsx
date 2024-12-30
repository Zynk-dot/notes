import React from 'react';
import { type Note } from '../types';
import { Clock } from 'lucide-react';

interface Props {
  note: Note;
}

export default function NoteCard({ note }: Props) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center text-gray-500">
          <Clock size={16} className="mr-2" />
          <span>{new Date(note.timestamp).toLocaleString()}</span>
        </div>
      </div>
      
      <div className="mb-4">
        <h3 className="text-lg font-semibold mb-2">Original Text</h3>
        <p className="text-gray-700">{note.text}</p>
      </div>

      {note.summary && (
        <div className="mb-4">
          <h3 className="text-lg font-semibold mb-2">Summary</h3>
          <p className="text-gray-700">{note.summary}</p>
        </div>
      )}

      {note.bullets.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-2">Key Points</h3>
          <ul className="list-disc list-inside text-gray-700">
            {note.bullets.map((bullet, index) => (
              <li key={index}>{bullet}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}