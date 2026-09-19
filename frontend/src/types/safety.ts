export interface ConfusionMatrix {
  TP: number
  TN: number
  FP: number
  FN: number
}

export interface SafetyMetrics {
  accuracy: number
  precision: number
  recall: number
  fnr: number
  fpr: number
}

export interface SafetyEvaluation {
  dataset_size: number
  confusion_matrix: ConfusionMatrix
  metrics: SafetyMetrics
  evaluation_type: string
  warning: string
}
