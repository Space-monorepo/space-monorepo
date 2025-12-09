export default function getCheckmarkColorClass(role?: string) {
    if (!role) return '';
    if (role.toLowerCase().includes('admin')) {
        return 'text-[#B79200]/40';
    }
    if (role.toLowerCase().includes('moderador') || role.toLowerCase().includes('moderator')) {
        return 'text-[#003349]';
    }
    if (role.toLowerCase().includes('líder') || role.toLowerCase().includes('leader')) {
        return 'text-black';
    }
    if (role.toLowerCase().includes('membro') || role.toLowerCase().includes('member')) {
        return 'text-black';
    }
    return 'text-black';
};