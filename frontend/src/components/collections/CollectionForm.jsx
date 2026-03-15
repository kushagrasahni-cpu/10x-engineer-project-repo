import { useState } from 'react'
import Button from '../shared/Button'
import './CollectionForm.css'

function CollectionForm({ onSubmit, onCancel }) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [error, setError] = useState('')

  function handleSubmit(e) {
    e.preventDefault()
    if (!name.trim()) {
      setError('Name is required')
      return
    }
    if (name.length > 100) {
      setError('Name must be under 100 characters')
      return
    }
    setError('')
    onSubmit({
      name: name.trim(),
      description: description.trim() || null,
    })
  }

  return (
    <form className="collection-form" onSubmit={handleSubmit}>
      <div className="collection-form__field">
        <label className="collection-form__label" htmlFor="cf-name">Name</label>
        <input
          id="cf-name"
          className={`collection-form__input ${error ? 'collection-form__input--error' : ''}`}
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g. Code Review Prompts"
          maxLength={100}
          autoFocus
        />
        {error && <span className="collection-form__error">{error}</span>}
      </div>

      <div className="collection-form__field">
        <label className="collection-form__label" htmlFor="cf-desc">
          Description (optional)
        </label>
        <input
          id="cf-desc"
          className="collection-form__input"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Brief description"
          maxLength={500}
        />
      </div>

      <div className="collection-form__actions">
        <Button type="submit" variant="primary">Create</Button>
        <Button variant="secondary" onClick={onCancel}>Cancel</Button>
      </div>
    </form>
  )
}

export default CollectionForm
