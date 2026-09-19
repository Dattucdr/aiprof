export default function Loading({
  message = "Loading...",
}: {
  message?: string
}) {
  return (
    <div className="flex items-center justify-center p-10">
      <div className="flex items-center space-x-3 text-sm text-slate-500">
        <div className="h-5 w-5 animate-spin rounded-full border-2 border-blue-600 border-t-transparent"></div>
        <span>{message}</span>
      </div>
    </div>
  )
}
