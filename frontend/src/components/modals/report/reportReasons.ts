export const REPORT_REASONS = [
  { value: 'discrimination', label: 'Discriminação' },
  { value: 'harassment', label: 'Assédio' },
  { value: 'hate_speech', label: 'Discurso de ódio' },
  { value: 'inappropriate_content', label: 'Conteúdo inapropriado' },
  { value: 'misinformation', label: 'Desinformação' },
  { value: 'sensitive_content', label: 'Conteúdo sensível' },
  { value: 'spam', label: 'Spam' },
  { value: 'threat', label: 'Ameaça' },
  { value: 'other', label: 'Outro' },
];

export type ReportReason = typeof REPORT_REASONS[number]['value'];
