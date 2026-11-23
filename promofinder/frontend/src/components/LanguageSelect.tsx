import { useLanguage } from '../i18n'

export default function LanguageSelect() {
  const { language, setLanguage, t } = useLanguage()

  const handleChange = (value: string) => {
    if (value === 'pt' || value === 'en' || value === 'es') setLanguage(value)
  }

  return (
    <select
      aria-label={t('preferences.language')}
      className="input h-10 w-auto min-w-24 px-2 text-sm"
      value={language}
      onChange={event => handleChange(event.target.value)}
    >
      <option value="pt">{t('preferences.portuguese')}</option>
      <option value="en">{t('preferences.english')}</option>
      <option value="es">{t('preferences.spanish')}</option>
    </select>
  )
}
