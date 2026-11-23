import { useLanguage } from '../i18n'
import { useTheme } from '../theme'

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()
  const { t } = useLanguage()

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className="grid h-10 w-10 shrink-0 place-items-center rounded-xl border border-border text-lg transition-colors hover:bg-surface"
      aria-label={theme === 'dark' ? t('shell.themeToLight') : t('shell.themeToDark')}
      title={theme === 'dark' ? t('shell.themeToLight') : t('shell.themeToDark')}
    >
      {theme === 'dark' ? '☼' : '☾'}
    </button>
  )
}
