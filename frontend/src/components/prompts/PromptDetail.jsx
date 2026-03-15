import Button from '../shared/Button'
import './PromptDetail.css'

function PromptDetail({ prompt, onEdit, onDelete, onClose }) {
  const variables = prompt.content.match(/\{\{(\w+)\}\}/g) || []

  return (
    <div className="prompt-detail">
      <div className="prompt-detail__header">
        <h2 className="prompt-detail__title">{prompt.title}</h2>
        <div className="prompt-detail__actions">
          <Button variant="primary" onClick={() => onEdit(prompt)}>Edit</Button>
          <Button variant="danger" onClick={() => onDelete(prompt.id)}>Delete</Button>
          <Button variant="secondary" onClick={onClose}>Close</Button>
        </div>
      </div>

      {prompt.description && (
        <p className="prompt-detail__desc">{prompt.description}</p>
      )}

      <div className="prompt-detail__section">
        <h3 className="prompt-detail__section-title">Content</h3>
        <pre className="prompt-detail__content">{prompt.content}</pre>
      </div>

      {variables.length > 0 && (
        <div className="prompt-detail__section">
          <h3 className="prompt-detail__section-title">Variables</h3>
          <div className="prompt-detail__vars">
            {variables.map((v, i) => (
              <span key={i} className="prompt-detail__var">{v}</span>
            ))}
          </div>
        </div>
      )}

      <div className="prompt-detail__meta">
        <span>Created: {new Date(prompt.created_at).toLocaleString()}</span>
        <span>Updated: {new Date(prompt.updated_at).toLocaleString()}</span>
      </div>
    </div>
  )
}

export default PromptDetail
