import './Header.css'

function Header({ onNewPrompt }) {
  return (
    <header className="header">
      <div className="header__brand">
        <h1 className="header__title">PromptLab</h1>
        <span className="header__subtitle">AI Prompt Engineering Platform</span>
      </div>
      <button className="header__btn" onClick={onNewPrompt}>
        + New Prompt
      </button>
    </header>
  )
}

export default Header
