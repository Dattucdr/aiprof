import { useEffect, useState } from "react"

import { getSafetyEvaluation } from "../api/safety"

import type {
  SafetyEvaluation as SafetyEvaluationType,
} from "../types/safety"


export default function SafetyEvaluation() {

  const [data, setData] =
    useState<SafetyEvaluationType | null>(null)

  const [loading, setLoading] =
    useState(true)

  const [error, setError] =
    useState("")


  useEffect(() => {
    loadEvaluation()
  }, [])


  async function loadEvaluation() {

    try {

      setLoading(true)
      setError("")

      const result =
        await getSafetyEvaluation()

      setData(result)

    } catch (err) {

      console.error(err)

      setError(
        "Failed to load safety evaluation."
      )

    } finally {

      setLoading(false)

    }
  }


  if (loading) {
    return (
      <div className="p-6">
        Loading safety evaluation...
      </div>
    )
  }


  if (!data) {
    return (
      <div className="p-6 text-red-600">
        {error || "Safety evaluation unavailable."}
      </div>
    )
  }


  const matrix =
    data.confusion_matrix

  const metrics =
    data.metrics


  return (

    <div className="space-y-6 p-6">

      {/* Header */}

      <div className="flex items-center justify-between">

        <div>

          <h1 className="text-2xl font-bold">
            Safety Evaluation
          </h1>

          <p className="mt-1 text-gray-500">
            Evaluation of AI escalation decisions.
          </p>

        </div>


        <button
          onClick={loadEvaluation}
          className="rounded-lg border px-4 py-2 hover:bg-gray-50 cursor-pointer"
        >
          Refresh
        </button>

      </div>


      {/* Warning */}

      <div className="rounded-xl border border-yellow-200 bg-yellow-50 p-5">

        <p className="font-semibold">
          {data.evaluation_type}
        </p>

        <p className="mt-1 text-sm text-gray-700">
          {data.warning}
        </p>

      </div>


      {/* Dataset */}

      <div className="rounded-xl border bg-white p-6 shadow-sm">

        <p className="text-sm text-gray-500">
          Evaluation Dataset
        </p>

        <p className="mt-2 text-3xl font-bold">
          {data.dataset_size}
        </p>

        <p className="mt-1 text-sm text-gray-500">
          synthetic evaluation cases
        </p>

      </div>


      {/* Confusion Matrix */}

      <section className="rounded-xl border bg-white p-6 shadow-sm">

        <h2 className="text-lg font-semibold">
          Confusion Matrix
        </h2>

        <div className="mt-5 grid grid-cols-2 gap-4">

          <MatrixCard
            label="True Positive"
            short="TP"
            value={matrix.TP}
          />

          <MatrixCard
            label="True Negative"
            short="TN"
            value={matrix.TN}
          />

          <MatrixCard
            label="False Positive"
            short="FP"
            value={matrix.FP}
          />

          <MatrixCard
            label="False Negative"
            short="FN"
            value={matrix.FN}
          />

        </div>

      </section>


      {/* Metrics */}

      <section className="rounded-xl border bg-white p-6 shadow-sm">

        <h2 className="text-lg font-semibold">
          Evaluation Metrics
        </h2>

        <div className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-5">

          <Metric
            label="Accuracy"
            value={metrics.accuracy}
          />

          <Metric
            label="Precision"
            value={metrics.precision}
          />

          <Metric
            label="Recall"
            value={metrics.recall}
          />

          <Metric
            label="FNR"
            value={metrics.fnr}
          />

          <Metric
            label="FPR"
            value={metrics.fpr}
          />

        </div>

      </section>


      {/* Safety Explanation */}

      <section className="rounded-xl border bg-white p-6 shadow-sm">

        <h2 className="text-lg font-semibold">
          Safety Metrics
        </h2>

        <div className="mt-4 space-y-4 text-sm text-gray-700">

          <p>
            <strong>False Negative (FN)</strong> means
            the system failed to identify a case that
            required escalation.
          </p>

          <p>
            <strong>False Negative Rate (FNR)</strong>{" "}
            measures the proportion of escalation-required
            cases that were missed.
          </p>

          <p>
            <strong>Recall</strong> measures how many of
            the escalation-required cases were detected.
          </p>

        </div>

      </section>

    </div>
  )
}


function MatrixCard({
  label,
  short,
  value,
}: {
  label: string
  short: string
  value: number
}) {

  return (

    <div className="rounded-xl border p-5">

      <div className="flex items-center justify-between">

        <p className="text-sm text-gray-500">
          {label}
        </p>

        <span className="rounded-full border px-2 py-1 text-xs">
          {short}
        </span>

      </div>

      <p className="mt-3 text-3xl font-bold">
        {value}
      </p>

    </div>

  )
}


function Metric({
  label,
  value,
}: {
  label: string
  value: number
}) {

  return (

    <div className="rounded-lg border p-4">

      <p className="text-sm text-gray-500">
        {label}
      </p>

      <p className="mt-2 text-2xl font-bold">
        {(value * 100).toFixed(2)}%
      </p>

    </div>

  )
}
