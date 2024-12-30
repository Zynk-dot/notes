export class ModelError extends Error {
  constructor(message: string, public originalError?: unknown) {
    super(message);
    this.name = 'ModelError';
  }
}