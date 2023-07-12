
class VacancyStatus:
    DRAFTING = 'drafting'
    OPENED = 'opened'
    CLOSED = 'closed'
    HELD = 'held'
    CANCELLED = 'cancelled'
    ARCHIVED = 'archived'


class SlackChannels:
    HR_AUTOMATION = 'hr-automation-reports'


PASSIVE = 'passive'
ACTIVE = 'active'


SOURCE_MAP = {
    'HeadHunter (отклик кандидата)': PASSIVE,
    'HeadHunter (ручной поиск) ': ACTIVE,
    'Job Board': PASSIVE,
    'Linkedin Network (active)': ACTIVE,
    'Linkedin Network (passive)': PASSIVE,
    'Linkedin Post': PASSIVE,
    'Linkedin Sourcing': ACTIVE,
    'Referral': PASSIVE,
    'Telegram Chat': PASSIVE,
    'Добавлено вручную': PASSIVE,
    'Хабр Карьера (отклик кандидата) ': PASSIVE,
    'Хабр Карьера (ручной поиск)': ACTIVE,
}
