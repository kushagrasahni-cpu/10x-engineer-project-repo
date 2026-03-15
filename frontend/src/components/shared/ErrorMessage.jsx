import './ErrorMessage.css'

function ErrorMessage({ message, onRetry }) {
  return (
    <div className="error-message" role="alert">
      <p className="error-message__text">{message}</p>
      {onRetry && (
        <button className="error-message__retry" onClick={onRetry}>
          Retry
        </button>
      )}
    </div>
  )
}

export default ErrorMessage
