import './PromptCard.css'

function PromptCard({ prompt, onClick, onDelete }) {
  const date = new Date(prompt.created_at).toLocaleDateString()

  return (
    <div className="prompt-card" onClick={() => onClick(prompt)}>
      <div className="prompt-card__header">
        <h3 className="prompt-card__title">{prompt.title}</h3>
        <button
          className="prompt-card__delete"
          onClick={(e) => {
            e.stopPropagation()
            onDelete(prompt.id)
          }}
          aria-label={`Delete ${prompt.title}`}
        >
          x
        </button>
      </div>
      {prompt.description && (
        <p className="prompt-card__desc">{prompt.description}</p>
      )}
      <p className="prompt-card__content">
        {prompt.content.length > 100
          ? prompt.content.slice(0, 100) + '...'
          : prompt.content}
      </p>
      <div className="prompt-card__footer">
        <span className="prompt-card__date">{date}</span>
      </div>
    </div>
  )
}

export default PromptCard
