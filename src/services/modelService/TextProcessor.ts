import * as tf from '@tensorflow/tfjs';

export class TextProcessor {
  clean(text: string): string {
    return text
      .trim()
      .replace(/\s+/g, ' ')
      .replace(/[^\w\s.,!?-]/g, '');
  }

  splitIntoSentences(text: string): string[] {
    return text
      .split(/[.!?]+/)
      .map(s => s.trim())
      .filter(s => s.length > 0);
  }

  async generateSummary(sentences: string[], embeddings: tf.Tensor): Promise<string> {
    const scores = await this.getSentenceScores(sentences, embeddings);
    const topSentences = this.getTopSentences(sentences, scores, 3);
    return topSentences.join('. ') + '.';
  }

  async generateBulletPoints(sentences: string[], embeddings: tf.Tensor): Promise<string[]> {
    const scores = await this.getSentenceScores(sentences, embeddings);
    return this.getTopSentences(sentences, scores, 5);
  }

  private async getSentenceScores(sentences: string[], embeddings: tf.Tensor): Promise<number[]> {
    return tf.tidy(() => {
      const sentenceEmbeddings = embeddings.unstack();
      const documentEmbedding = embeddings.mean(0);
      
      return sentenceEmbeddings.map(sentenceEmbedding => 
        documentEmbedding.dot(sentenceEmbedding).dataSync()[0]
      );
    });
  }

  private getTopSentences(sentences: string[], scores: number[], count: number): string[] {
    return sentences
      .map((sentence, index) => ({ sentence, score: scores[index] }))
      .sort((a, b) => b.score - a.score)
      .slice(0, count)
      .map(({ sentence }) => sentence.trim());
  }
}