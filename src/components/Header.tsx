import React from 'react';
import { Brain, Github } from 'lucide-react';
import ThemeToggle from './ThemeToggle';

export default function Header() {
  return (
    <header className="bg-white dark:bg-gray-800 shadow-sm">
      <div className="max-w-4xl mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Brain className="text-blue-500" size={32} />
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">AI Note Taker</h1>
          </div>
          <div className="flex items-center space-x-4">
            <ThemeToggle />
            <a
              href="https://github.com/Zynk-dot/notes"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
            >
              <Github size={24} />
            </a>
          </div>
        </div>
      </div>
    </header>
  );
}