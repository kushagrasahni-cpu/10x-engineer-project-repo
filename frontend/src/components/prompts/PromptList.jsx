import PromptCard from './PromptCard'
import './PromptList.css'

function PromptList({ prompts, onSelect, onDelete }) {
  if (prompts.length === 0) {
    return (
      <div className="prompt-list__empty">
        <p>No prompts yet.</p>
        <p className="prompt-list__empty-hint">
          Create your first prompt to get started.
        </p>
      </div>
    )
  }

  return (
    <div className="prompt-list">
      {prompts.map((prompt) => (
        <PromptCard
          key={prompt.id}
          prompt={prompt}
          onClick={onSelect}
          onDelete={onDelete}
        />
      ))}
    </div>
  )
}

export default PromptList
