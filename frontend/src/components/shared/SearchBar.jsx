import './SearchBar.css'

function SearchBar({ value, onChange, placeholder = 'Search prompts...' }) {
  return (
    <input
      className="search-bar"
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      aria-label="Search"
    />
  )
}

export default SearchBar
