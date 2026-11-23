import LanguageSelect from './LanguageSelect'
import ThemeToggle from './ThemeToggle'

export default function AppearanceControls() {
  return (
    <div className="fixed right-4 top-4 z-40 flex items-center gap-2">
      <LanguageSelect />
      <ThemeToggle />
    </div>
  )
}
