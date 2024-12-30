import * as tf from '@tensorflow/tfjs';
import * as use from '@tensorflow-models/universal-sentence-encoder';
import { ModelError } from '../../utils/errors';
import { EmbeddingCache } from './EmbeddingCache';
import { TextProcessor } from './TextProcessor';
import { TensorManager } from './TensorManager';

export class ModelService {
  private static instance: ModelService;
  private useModel: use.UniversalSentenceEncoder | null = null;
  private isLoading = false;
  private modelLoadPromise: Promise<void> | null = null;
  private embeddingCache: EmbeddingCache;
  private tensorManager: TensorManager;
  private textProcessor: TextProcessor;

  private constructor() {
    this.embeddingCache = new EmbeddingCache();
    this.tensorManager = new TensorManager();
    this.textProcessor = new TextProcessor();
    this.initializeTensorflow();
  }

  private initializeTensorflow(): void {
    tf.setBackend('webgl');
    tf.ready().then(() => {
      tf.tidy(() => tf.zeros([1]));
    });
  }

  static getInstance(): ModelService {
    if (!ModelService.instance) {
      ModelService.instance = new ModelService();
    }
    return ModelService.instance;
  }

  async loadModels(): Promise<void> {
    if (this.useModel) return;
    if (this.modelLoadPromise) return this.modelLoadPromise;

    this.isLoading = true;
    this.modelLoadPromise = use.load({ maxBatchSize: 8 })
      .then(model => { this.useModel = model; })
      .catch(error => { throw new ModelError('Failed to initialize model', error); })
      .finally(() => {
        this.isLoading = false;
        this.modelLoadPromise = null;
      });

    return this.modelLoadPromise;
  }

  async generateEmbeddings(text: string): Promise<tf.Tensor> {
    const cached = this.embeddingCache.get(text);
    if (cached) return cached;

    if (!this.useModel) {
      await this.loadModels();
    }
    
    if (!this.useModel) {
      throw new ModelError('Model not loaded');
    }

    try {
      const embedding = await this.useModel.embed(text);
      this.embeddingCache.set(text, embedding);
      return embedding;
    } catch (error) {
      throw new ModelError('Failed to generate embeddings', error);
    }
  }

  async summarizeText(text: string): Promise<string> {
    return this.tensorManager.tidy(async () => {
      try {
        const cleanedText = this.textProcessor.clean(text);
        const embeddings = await this.generateEmbeddings(cleanedText);
        const sentences = this.textProcessor.splitIntoSentences(cleanedText);
        const summary = await this.textProcessor.generateSummary(sentences, embeddings);
        return summary;
      } catch (error) {
        throw new ModelError('Failed to generate summary', error);
      }
    });
  }

  async generateBulletPoints(text: string): Promise<string[]> {
    return this.tensorManager.tidy(async () => {
      try {
        const cleanedText = this.textProcessor.clean(text);
        const embeddings = await this.generateEmbeddings(cleanedText);
        const sentences = this.textProcessor.splitIntoSentences(cleanedText);
        const bullets = await this.textProcessor.generateBulletPoints(sentences, embeddings);
        return bullets;
      } catch (error) {
        throw new ModelError('Failed to generate bullet points', error);
      }
    });
  }

  dispose(): void {
    this.embeddingCache.dispose();
    this.tensorManager.dispose();
  }
}