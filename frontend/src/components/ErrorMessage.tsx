interface Props {
  message: string
  onRetry?: () => void
}

export default function ErrorMessage({
  message,
  onRetry,
}: Props) {
  return (
    <div className="rounded-xl border border-red-200 bg-red-50 p-5">
      <p className="font-medium text-red-700">
        {message}
      </p>

      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-3 rounded-lg border border-red-300 px-4 py-2 text-sm text-red-800 hover:bg-red-100 cursor-pointer"
        >
          Retry
        </button>
      )}
    </div>
  )
}
