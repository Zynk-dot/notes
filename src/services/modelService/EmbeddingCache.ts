import * as tf from '@tensorflow/tfjs';

export class EmbeddingCache {
  private cache: Map<string, tf.Tensor> = new Map();
  private readonly maxSize = 50;

  get(text: string): tf.Tensor | null {
    const cached = this.cache.get(text);
    if (cached) {
      return cached.clone();
    }
    return null;
  }

  set(text: string, embedding: tf.Tensor): void {
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      const tensor = this.cache.get(firstKey);
      if (tensor) tensor.dispose();
      this.cache.delete(firstKey);
    }
    this.cache.set(text, embedding.clone());
  }

  dispose(): void {
    for (const tensor of this.cache.values()) {
      tensor.dispose();
    }
    this.cache.clear();
  }
}