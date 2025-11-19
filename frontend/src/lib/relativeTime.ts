// Função utilitária para mostrar tempo relativo (ex: '1h atrás', '20 min atrás')
export function getRelativeTime(dateString: string) {
    const now = new Date();
    const date = new Date(dateString);
    // Ajuste para horário de Brasília (GMT-3)
    date.setHours(date.getHours() - 3);
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return 'agora mesmo';
    if (diffMins < 60) return `${diffMins} min atrás`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h atrás`;
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays === 1) return 'ontem';
    if (diffDays < 7) return `${diffDays} dias atrás`;
    // Se for mais de uma semana, mostra a data
    return date.toLocaleDateString('pt-BR');
}
