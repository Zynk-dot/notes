export interface Note {
  id: string;
  text: string;
  summary: string | null;
  bullets: string[];
  timestamp: Date;
}

export interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}