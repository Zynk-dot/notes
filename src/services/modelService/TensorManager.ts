import * as tf from '@tensorflow/tfjs';

export class TensorManager {
  async tidy<T>(fn: () => Promise<T>): Promise<T> {
    return tf.tidy(fn);
  }

  dispose(): void {
    tf.disposeVariables();
  }
}