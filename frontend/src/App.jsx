import { useState, useEffect, useCallback } from 'react'
import './App.css'

import Header from './components/layout/Header'
import Sidebar from './components/layout/Sidebar'
import SearchBar from './components/shared/SearchBar'
import LoadingSpinner from './components/shared/LoadingSpinner'
import ErrorMessage from './components/shared/ErrorMessage'
import Modal from './components/shared/Modal'

import PromptList from './components/prompts/PromptList'
import PromptDetail from './components/prompts/PromptDetail'
import PromptForm from './components/prompts/PromptForm'
import CollectionForm from './components/collections/CollectionForm'

import * as promptsApi from './api/prompts'
import * as collectionsApi from './api/collections'

function App() {
  const [prompts, setPrompts] = useState([])
  const [collections, setCollections] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [selectedCollectionId, setSelectedCollectionId] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedPrompt, setSelectedPrompt] = useState(null)

  const [showPromptForm, setShowPromptForm] = useState(false)
  const [editingPrompt, setEditingPrompt] = useState(null)
  const [showCollectionForm, setShowCollectionForm] = useState(false)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [promptsData, collectionsData] = await Promise.all([
        promptsApi.getPrompts({
          collectionId: selectedCollectionId,
          search: searchQuery || undefined,
        }),
        collectionsApi.getCollections(),
      ])
      setPrompts(promptsData.prompts)
      setCollections(collectionsData.collections)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [selectedCollectionId, searchQuery])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  async function handleCreatePrompt(data) {
    try {
      await promptsApi.createPrompt(data)
      setShowPromptForm(false)
      fetchData()
    } catch (err) {
      alert(err.message)
    }
  }

  async function handleUpdatePrompt(data) {
    try {
      await promptsApi.updatePrompt(editingPrompt.id, data)
      setEditingPrompt(null)
      setShowPromptForm(false)
      setSelectedPrompt(null)
      fetchData()
    } catch (err) {
      alert(err.message)
    }
  }

  async function handleDeletePrompt(id) {
    if (!confirm('Delete this prompt?')) return
    try {
      await promptsApi.deletePrompt(id)
      if (selectedPrompt?.id === id) setSelectedPrompt(null)
      fetchData()
    } catch (err) {
      alert(err.message)
    }
  }

  async function handleCreateCollection(data) {
    try {
      await collectionsApi.createCollection(data)
      setShowCollectionForm(false)
      fetchData()
    } catch (err) {
      alert(err.message)
    }
  }

  async function handleDeleteCollection(id) {
    if (!confirm('Delete this collection?')) return
    try {
      await collectionsApi.deleteCollection(id)
      if (selectedCollectionId === id) setSelectedCollectionId(null)
      fetchData()
    } catch (err) {
      alert(err.message)
    }
  }

  function handleSelectPrompt(prompt) {
    setSelectedPrompt(prompt)
  }

  function handleEditPrompt(prompt) {
    setEditingPrompt(prompt)
    setShowPromptForm(true)
  }

  function handleNewPrompt() {
    setEditingPrompt(null)
    setShowPromptForm(true)
  }

  function handleCloseForm() {
    setShowPromptForm(false)
    setEditingPrompt(null)
  }

  return (
    <div className="app">
      <div className="app__sidebar">
        <Sidebar
          collections={collections}
          selectedCollectionId={selectedCollectionId}
          onSelectCollection={setSelectedCollectionId}
          onNewCollection={() => setShowCollectionForm(true)}
          onDeleteCollection={handleDeleteCollection}
        />
      </div>

      <main className="app__main">
        <Header onNewPrompt={handleNewPrompt} />

        <div className="app__content">
          <div className="app__toolbar">
            <SearchBar value={searchQuery} onChange={setSearchQuery} />
          </div>

          {loading && <LoadingSpinner />}
          {error && <ErrorMessage message={error} onRetry={fetchData} />}
          {!loading && !error && !selectedPrompt && (
            <PromptList
              prompts={prompts}
              onSelect={handleSelectPrompt}
              onDelete={handleDeletePrompt}
            />
          )}
          {!loading && !error && selectedPrompt && (
            <PromptDetail
              prompt={selectedPrompt}
              onEdit={handleEditPrompt}
              onDelete={handleDeletePrompt}
              onClose={() => setSelectedPrompt(null)}
            />
          )}
        </div>
      </main>

      {showPromptForm && (
        <Modal
          title={editingPrompt ? 'Edit Prompt' : 'New Prompt'}
          onClose={handleCloseForm}
        >
          <PromptForm
            initial={editingPrompt}
            collections={collections}
            onSubmit={editingPrompt ? handleUpdatePrompt : handleCreatePrompt}
            onCancel={handleCloseForm}
          />
        </Modal>
      )}

      {showCollectionForm && (
        <Modal title="New Collection" onClose={() => setShowCollectionForm(false)}>
          <CollectionForm
            onSubmit={handleCreateCollection}
            onCancel={() => setShowCollectionForm(false)}
          />
        </Modal>
      )}
    </div>
  )
}

export default App
