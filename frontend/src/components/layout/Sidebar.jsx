import './Sidebar.css'

function Sidebar({
  collections,
  selectedCollectionId,
  onSelectCollection,
  onNewCollection,
  onDeleteCollection,
}) {
  return (
    <aside className="sidebar">
      <div className="sidebar__header">
        <h2 className="sidebar__title">Collections</h2>
        <button className="sidebar__add-btn" onClick={onNewCollection}>
          +
        </button>
      </div>

      <ul className="sidebar__list">
        <li
          className={`sidebar__item ${!selectedCollectionId ? 'sidebar__item--active' : ''}`}
          onClick={() => onSelectCollection(null)}
        >
          All Prompts
        </li>
        {collections.map((col) => (
          <li
            key={col.id}
            className={`sidebar__item ${selectedCollectionId === col.id ? 'sidebar__item--active' : ''}`}
            onClick={() => onSelectCollection(col.id)}
          >
            <span className="sidebar__item-name">{col.name}</span>
            <button
              className="sidebar__delete-btn"
              onClick={(e) => {
                e.stopPropagation()
                onDeleteCollection(col.id)
              }}
              aria-label={`Delete ${col.name}`}
            >
              x
            </button>
          </li>
        ))}
      </ul>
    </aside>
  )
}

export default Sidebar
