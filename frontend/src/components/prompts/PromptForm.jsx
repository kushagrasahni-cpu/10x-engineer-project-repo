import { useState, useEffect } from 'react'
import Button from '../shared/Button'
import './PromptForm.css'

function PromptForm({ initial, collections, onSubmit, onCancel }) {
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [description, setDescription] = useState('')
  const [collectionId, setCollectionId] = useState('')
  const [errors, setErrors] = useState({})

  useEffect(() => {
    if (initial) {
      setTitle(initial.title || '')
      setContent(initial.content || '')
      setDescription(initial.description || '')
      setCollectionId(initial.collection_id || '')
    }
  }, [initial])

  function validate() {
    const newErrors = {}
    if (!title.trim()) newErrors.title = 'Title is required'
    if (title.length > 200) newErrors.title = 'Title must be under 200 characters'
    if (!content.trim()) newErrors.content = 'Content is required'
    if (description.length > 500) newErrors.description = 'Description must be under 500 characters'
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  function handleSubmit(e) {
    e.preventDefault()
    if (!validate()) return
    onSubmit({
      title: title.trim(),
      content: content.trim(),
      description: description.trim() || null,
      collection_id: collectionId || null,
    })
  }

  return (
    <form className="prompt-form" onSubmit={handleSubmit}>
      <div className="prompt-form__field">
        <label className="prompt-form__label" htmlFor="pf-title">Title</label>
        <input
          id="pf-title"
          className={`prompt-form__input ${errors.title ? 'prompt-form__input--error' : ''}`}
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="e.g. Code Review Assistant"
          maxLength={200}
        />
        {errors.title && <span className="prompt-form__error">{errors.title}</span>}
      </div>

      <div className="prompt-form__field">
        <label className="prompt-form__label" htmlFor="pf-content">Content</label>
        <textarea
          id="pf-content"
          className={`prompt-form__textarea ${errors.content ? 'prompt-form__input--error' : ''}`}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Write your prompt template... Use {{variable}} for placeholders"
          rows={6}
        />
        {errors.content && <span className="prompt-form__error">{errors.content}</span>}
      </div>

      <div className="prompt-form__field">
        <label className="prompt-form__label" htmlFor="pf-desc">Description (optional)</label>
        <input
          id="pf-desc"
          className="prompt-form__input"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Brief description of this prompt"
          maxLength={500}
        />
        {errors.description && <span className="prompt-form__error">{errors.description}</span>}
      </div>

      <div className="prompt-form__field">
        <label className="prompt-form__label" htmlFor="pf-col">Collection (optional)</label>
        <select
          id="pf-col"
          className="prompt-form__select"
          value={collectionId}
          onChange={(e) => setCollectionId(e.target.value)}
        >
          <option value="">None</option>
          {collections.map((col) => (
            <option key={col.id} value={col.id}>{col.name}</option>
          ))}
        </select>
      </div>

      <div className="prompt-form__actions">
        <Button type="submit" variant="primary">
          {initial ? 'Update' : 'Create'}
        </Button>
        <Button variant="secondary" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </form>
  )
}

export default PromptForm
