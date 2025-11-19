// Função utilitária para classes do badge de role
const getRoleBadgeClasses = (role?: string) => {
    if (!role) return '';
    if (role.toLowerCase().includes('admin')) {
        return 'bg-[#B79200]/40 text-[#4A3800]';
    }
    if (role.toLowerCase().includes('moderador') || role.toLowerCase().includes('moderator')) {
        return 'bg-[#004E64]/40 text-[#003349]';
    }
    if (role.toLowerCase().includes('líder') || role.toLowerCase().includes('leader')) {
        return 'bg-neutral-800 text-zinc-100';
    }
    if (role.toLowerCase().includes('membro') || role.toLowerCase().includes('member')) {
        return 'bg-neutral-800 text-zinc-100';
    }
    return 'bg-neutral-800 text-zinc-100';
};

export default getRoleBadgeClasses;