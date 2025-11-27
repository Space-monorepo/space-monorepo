import os
from pathlib import Path

import app.core.init_db  # noqa: F401 - garante que os modelos estão registrados
from app.api.communities.model import Community, CommunityMember
from app.api.users.schema import UserCreate, UserStatusEnum
from app.api.users.service import UserService
from app.core.database import get_db
from app.core.transaction import TransactionManager

STATIC_AVATAR_SUBDIR = Path('avatars/puc_campinas')
STATIC_AVATAR_FS_DIR = (
    Path(__file__).resolve().parent.parent / 'static' / STATIC_AVATAR_SUBDIR
)
BACKEND_BASE_URL = os.getenv('BACKEND_BASE_URL', 'http://localhost:8000').rstrip('/')
STATIC_AVATAR_URL_BASE = f'{BACKEND_BASE_URL}/static/{STATIC_AVATAR_SUBDIR.as_posix()}'


def init_puc_campinas():
    db = next(get_db())
    role_map = {
        'membro': 'member',
        'administrador': 'admin',
        'moderador': 'moderator',
    }
    users_payload = [
        {
            'username': 'eliane',
            'name': 'Eliane',
            'email': 'eliane@space.com',
            'password': 'elianepassword123',
            'role': 'membro',
            'image_file': 'icons8-maxine-mayfield.svg',
            'bio': 'Entusiasta da PUC-Campinas apaixonada por projetos colaborativos.',
        },
        {
            'username': 'orandi',
            'name': 'Orandi',
            'email': 'orandi@space.com',
            'password': 'orandipassword123',
            'role': 'membro',
            'image_file': 'icons8-walter-white.svg',
            'bio': 'Curador de conteúdo sobre inovação e pesquisa acadêmica.',
        },
        {
            'username': 'picolo',
            'name': 'Picolo',
            'email': 'picolo@space.com',
            'password': 'picolopassword123',
            'role': 'membro',
            'image_file': 'icons8-sunny.svg',
            'bio': 'Responsável por mobilizar estudantes para ações comunitárias.',
        },
        {
            'username': 'dimas',
            'name': 'Dimas',
            'email': 'dimas@space.com',
            'password': 'dimaspassword123',
            'role': 'membro',
            'image_file': 'icons8-super-mario.svg',
            'bio': 'Mentor em iniciativas de tecnologia social dentro do campus.',
        },
        {
            'username': 'space',
            'name': 'Space',
            'email': 'space@space.com',
            'password': 'spacepassword123',
            'role': 'administrador',
            'image_file': 'icons8-mascara-dos-anonymous.svg',
            'bio': 'Administrador geral da comunidade PUC-Campinas no Space.',
        },
        {
            'username': 'spamod',
            'name': 'SpaMod',
            'email': 'spamod@space.com',
            'password': 'spacepassword123',
            'role': 'moderador',
            'image_file': 'icons8-comando.svg',
            'bio': 'Moderador dedicado a manter interações saudáveis na comunidade.',
        },
    ]

    try:
        with TransactionManager(db) as tm:
            user_service = UserService(tm)

            community = Community(
                name='PUC-Campinas',
                description='Rede interna para projetos acadêmicos, extensão e eventos da universidade.',
                type_community='university',
            )
            db.add(community)
            db.commit()
            db.refresh(community)
            print(f'Comunidade {community.name} criada com sucesso!')

            created_users = []
            for payload in users_payload:
                image_path = STATIC_AVATAR_FS_DIR / payload['image_file']
                if not image_path.exists():
                    raise FileNotFoundError(
                        f'Arquivo de avatar não encontrado: {image_path}. '
                        'Certifique-se de executar o seed após copiar os arquivos.'
                    )

                user_data = UserCreate(
                    username=payload['username'],
                    name=payload['name'],
                    email=payload['email'],
                    hashed_password=payload['password'],
                    profile_image_url=f'{STATIC_AVATAR_URL_BASE}/{payload["image_file"]}',
                    bio=payload['bio'],
                    status=UserStatusEnum.ACTIVE,
                )
                user = user_service.create_user(user_data)
                created_users.append(
                    {
                        'user': user,
                        'role': role_map.get(payload['role'].lower(), payload['role']),
                    }
                )
                print(f'Usuário {user.name} criado com sucesso (ID: {user.id})')

            for created in created_users:
                membership = CommunityMember(
                    user_id=created['user'].id,
                    community_id=community.id,
                    role=created['role'],
                )
                db.add(membership)
                db.commit()
                db.refresh(membership)
                print(
                    f'Membro vinculado: {created["user"].name} como {created["role"]} '
                    f'(CommunityMember ID: {membership.id})'
                )

            print('Seed da comunidade PUC-Campinas finalizado com sucesso.')
    except Exception as error:
        print(f'Erro ao inicializar dados da PUC-Campinas: {error}')


if __name__ == '__main__':
    init_puc_campinas()

