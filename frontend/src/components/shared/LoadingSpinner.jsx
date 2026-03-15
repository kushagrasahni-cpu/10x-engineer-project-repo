import './LoadingSpinner.css'

function LoadingSpinner() {
  return (
    <div className="spinner-container">
      <div className="spinner" role="status" aria-label="Loading" />
    </div>
  )
}

export default LoadingSpinner
